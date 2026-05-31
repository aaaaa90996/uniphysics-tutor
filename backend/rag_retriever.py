"""RAG 知识库检索模块

使用 Chroma 作为向量数据库，sentence-transformers 本地嵌入。
支持从 knowledge_base/ 目录加载 Markdown 文件并分块索引。
"""

import os
import re
import hashlib
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from config import settings

# ── 文本分块 ─────────────────────────────────────────────

CHUNK_SIZE = 800      # 每块约 800 字符
CHUNK_OVERLAP = 150   # 块间重叠


def _split_markdown(text: str, source: str) -> list[dict]:
    """将 Markdown 文本切分为可索引的文本块"""
    chunks = []

    # 按 ## 标题分割
    sections = re.split(r"\n(?=## )", text)

    for section in sections:
        # 提取标题作为元数据
        title_match = re.match(r"^# (.+)", section)
        title = title_match.group(1).strip() if title_match else source

        # 如果节过长，进一步按段落切
        if len(section) > CHUNK_SIZE:
            paragraphs = section.split("\n\n")
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) < CHUNK_SIZE:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append({
                            "content": current_chunk.strip(),
                            "metadata": {"title": title, "source": source},
                        })
                    current_chunk = para + "\n\n"
            if current_chunk.strip():
                chunks.append({
                    "content": current_chunk.strip(),
                    "metadata": {"title": title, "source": source},
                })
        else:
            if section.strip():
                chunks.append({
                    "content": section.strip(),
                    "metadata": {"title": title, "source": source},
                })

    return chunks


# ── Embedding 函数（本地模型）───────────────────────────

_embedding_function: Optional[embedding_functions.SentenceTransformerEmbeddingFunction] = None


def _get_embedding_function():
    """获取 embedding 函数，优先使用本地模型，否则用 Chroma 内置 ONNX 模型"""
    global _embedding_function
    if _embedding_function is None:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "")
        if model_name:
            try:
                from chromadb.utils import embedding_functions as ef
                _embedding_function = ef.SentenceTransformerEmbeddingFunction(
                    model_name=model_name,
                )
                print(f"[RAG] Embedding model loaded: {model_name}")
            except Exception as e:
                print(f"[RAG] Failed to load '{model_name}': {e}")
                print("[RAG] Falling back to default all-MiniLM-L6-v2 (ONNX)...")
                _embedding_function = embedding_functions.DefaultEmbeddingFunction()
        else:
            # 默认用 Chroma 内置的 all-MiniLM-L6-v2（ONNX，无需 PyTorch）
            print("[RAG] Using default embedding: all-MiniLM-L6-v2 (ONNX)")
            _embedding_function = embedding_functions.DefaultEmbeddingFunction()
    return _embedding_function


# ── Chroma 集合管理 ──────────────────────────────────────

_chroma_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None


def _get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


def _get_collection() -> chromadb.Collection:
    global _collection
    client = _get_chroma_client()
    ef = _get_embedding_function()
    _collection = client.get_or_create_collection(
        name="uniphysics_knowledge",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


# ── 索引构建 ─────────────────────────────────────────────

def _compute_content_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def build_index(force: bool = False) -> int:
    """构建/更新知识库索引。返回索引的文档数。"""
    collection = _get_collection()

    existing = collection.get()
    existing_hashes = set()
    if existing["metadatas"] and not force:
        for meta in existing["metadatas"]:
            if meta and "content_hash" in meta:
                existing_hashes.add(meta["content_hash"])

    kb_path = settings.KNOWLEDGE_BASE_PATH
    if not os.path.exists(kb_path):
        print(f"[RAG] Knowledge base not found: {kb_path}")
        return 0

    all_chunks = []
    md_files = []
    for root, _, files in os.walk(kb_path):
        for fname in files:
            if fname.endswith(".md"):
                md_files.append(os.path.join(root, fname))

    for filepath in md_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        rel_path = os.path.relpath(filepath, kb_path)
        chunks = _split_markdown(content, rel_path)

        for chunk in chunks:
            content_hash = _compute_content_hash(chunk["content"])
            if force or content_hash not in existing_hashes:
                chunk["metadata"]["content_hash"] = content_hash
                all_chunks.append(chunk)

    if not all_chunks:
        print("[RAG] No new documents to index.")
        return collection.count()

    texts = [c["content"] for c in all_chunks]
    metadatas = [c["metadata"] for c in all_chunks]
    ids = [f"chunk_{i}" for i in range(
        collection.count(),
        collection.count() + len(all_chunks),
    )]

    print(f"[RAG] Indexing {len(texts)} chunks from {len(md_files)} files with local embeddings...")

    # 分批写入（Chroma 有批量限制）
    BATCH = 100
    for i in range(0, len(all_chunks), BATCH):
        batch_end = min(i + BATCH, len(all_chunks))
        collection.add(
            ids=ids[i:batch_end],
            documents=texts[i:batch_end],
            metadatas=metadatas[i:batch_end],
        )

    print(f"[RAG] Indexed {len(all_chunks)} chunks from {len(md_files)} files.")
    return collection.count()


# ── 检索 ─────────────────────────────────────────────────

def retrieve(
    query: str,
    course: Optional[str] = None,
    top_k: int = 5,
) -> list[dict]:
    """检索与查询最相关的知识片段"""
    collection = _get_collection()

    if collection.count() == 0:
        print("[RAG] Collection empty, building index...")
        build_index()

    if collection.count() == 0:
        return []

    where_filter = None
    if course:
        course_map = {
            "mechanics": "mechanics",
            "electromagnetism": "electromagnetism",
            "oscillation": "oscillation",
            "thermodynamics": "thermodynamics",
            "optics": "optics",
        }
        folder = course_map.get(course, course)
        where_filter = {"source": {"$contains": folder}}

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
        where=where_filter,
    )

    chunks = []
    if results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            dist = results["distances"][0][i] if results["distances"] else 0
            chunks.append({
                "content": doc,
                "source": meta.get("source", "unknown"),
                "title": meta.get("title", ""),
                "score": round(1 - dist, 4) if dist else 1.0,
            })

    return chunks


def get_collection_stats() -> dict:
    """获取知识库统计信息"""
    collection = _get_collection()
    return {
        "total_chunks": collection.count(),
        "name": collection.name,
    }
