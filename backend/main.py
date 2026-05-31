"""UniPhysics Tutor 后端 API

FastAPI 服务，提供物理问答、解题、诊断、出题和知识检索接口。
"""

import json
import re
import threading
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas import (
    ChatRequest, ChatResponse,
    SolveRequest, SolveResponse,
    DiagnoseRequest, DiagnoseResponse,
    ExerciseRequest, ExerciseResponse, ExerciseItem,
    RetrieveRequest, RetrieveResponse, RetrieveChunk,
    HealthResponse, ErrorResponse,
)
from llm_client import get_llm_client
import prompt_loader as pl
from prompt_loader import (
    get_system_prompt, get_solver_prompt, get_diagnose_prompt,
    get_exercise_prompt, get_rewrite_prompt,
)
from rag_retriever import retrieve, build_index, get_collection_stats
from physics_validator import validate_physics_answer, validate_and_rewrite


# ── 应用生命周期 ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时在后台构建知识库索引"""
    print("[Startup] Building knowledge base index in background...")
    def _build():
        try:
            n = build_index()
            print(f"[Startup] Knowledge base ready: {n} chunks indexed.")
        except Exception as e:
            print(f"[Startup] Knowledge base index failed: {e}")
            print("[Startup] The API will still work but RAG may be unavailable.")
    t = threading.Thread(target=_build, daemon=True)
    t.start()
    yield


app = FastAPI(
    title="UniPhysics Tutor API",
    description="本科物理数字人智能助教后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 辅助函数 ──────────────────────────────────────────────

def _build_rag_context(chunks: list[dict]) -> str:
    """将检索到的知识片段拼接为 LLM 上下文"""
    if not chunks:
        return ""
    parts = ["## 知识库参考内容\n"]
    for i, chunk in enumerate(chunks, 1):
        src = chunk.get("source", "unknown")
        parts.append(f"### 参考 {i}（来源：{src}）\n{chunk['content']}\n")
    return "\n".join(parts)


def _construct_chat_message(
    user_message: str,
    mode: str,
    course: Optional[str],
    rag_context: str,
) -> str:
    """构造发给 LLM 的完整消息"""
    parts = [f"学生问题：{user_message}"]

    if course:
        course_names = {
            "mechanics": "力学",
            "electromagnetism": "电磁学",
            "oscillation": "振动与波",
            "thermodynamics": "热学",
            "optics": "光学",
        }
        parts.append(f"课程模块：{course_names.get(course, course)}")

    if mode == "guided":
        parts.append(
            "\n注意：当前为引导模式。请先给学生提示，不要直接给出完整答案。"
            "给学生机会自己思考后再逐步深入。如果学生卡住，给更具体的提示。"
        )
    elif mode == "full":
        parts.append("\n注意：当前为完整解题模式，请给出完整的、分步骤的解答。")

    if rag_context:
        parts.append(f"\n{rag_context}")
        parts.append("请基于以上知识库参考内容回答。如果知识库中没有足够依据，请明确说明。")

    return "\n\n".join(parts)


def _parse_structured_json(raw_answer: str) -> list[dict]:
    """从 LLM 回答中解析结构化 JSON。
    多层回退策略：
    1. 直接解析完整 JSON
    2. 从 markdown 代码块中提取 JSON
    3. 用正则提取最外层 JSON 对象
    4. 智能分段：按 ## 标题拆分原始 Markdown，每段作为独立 section
    5. 最后手段：整段作为一个 fallback
    """
    text = raw_answer.strip()

    # ── 策略 1：去掉 markdown ```json 包裹后直接解析 ──
    cleaned = text
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict) and "sections" in data:
            return data["sections"]
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, ValueError):
        pass

    # ── 策略 2：用正则找最外层 { "sections": [...] } ──
    # 使用贪婪匹配找到完整的 JSON 块
    match = re.search(r'\{\s*"sections"\s*:\s*\[', text)
    if match:
        start = match.start()
        # 从 start 开始，逐字符追踪括号深度找到匹配的 }
        depth = 0
        end = start
        for i, ch in enumerate(text[start:], start):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end > start:
            try:
                data = json.loads(text[start:end])
                if isinstance(data, dict) and "sections" in data:
                    return data["sections"]
            except (json.JSONDecodeError, ValueError):
                pass

    # ── 策略 3：智能分段 ──
    # 按 ## 标题拆分 Markdown，每段做成一个结构化 section
    sections = []
    # 按 ## / ### 标题切分
    parts = re.split(r'\n(?=#{2,3}\s+)', text)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # 提取标题
        title_match = re.match(r'#{2,3}\s+(.+)', part)
        title = title_match.group(1).strip() if title_match else None
        content = re.sub(r'^#{2,3}\s+.+\n?', '', part).strip()

        # 检测是否为公式块：包含 $$...$$ 或 $...$ 模式
        has_display_math = bool(re.search(r'\$\$[^$]+\$\$', content))
        has_inline_math = bool(re.search(r'\$[^$]+\$', content))

        if has_display_math or has_inline_math:
            # 提取第一个 $$...$$ 中的公式
            formula_match = re.search(r'\$\$\s*(.+?)\s*\$\$', content, re.DOTALL)
            formula = formula_match.group(1).strip() if formula_match else None
            # 去掉公式后的文字作为解释
            explanation = content
            if formula_match:
                explanation = content[formula_match.end():].strip()
                explanation = re.sub(r'\$\$|\$', '', explanation).strip()
            sections.append({
                "type": "formula_block",
                "title": title or "公式",
                "law_name": title,
                "formula": formula or content,
                "explanation": explanation if explanation != formula else "",
            })
        else:
            sections.append({
                "type": "concepts",
                "title": title or "回答",
                "content": content,
            })

    if sections:
        return sections

    # ── 策略 4：最后手段，整段作为 fallback（但清洗过） ──
    # 至少去掉最脏的 Markdown 标记
    clean_content = re.sub(r'\*\*|\*|#{1,4}\s*|`{1,3}', '', text)
    return [{
        "type": "fallback",
        "title": "回答",
        "content": clean_content,
    }]


# ── API 接口 ──────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    llm = get_llm_client()
    try:
        stats = get_collection_stats()
        kb_loaded = stats["total_chunks"] > 0
    except Exception:
        kb_loaded = False

    return HealthResponse(
        status="ok",
        version="0.1.0",
        llm_configured=llm.is_configured(),
        knowledge_base_loaded=kb_loaded,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """概念讲解对话"""
    llm = get_llm_client()
    if not llm.is_configured():
        raise HTTPException(status_code=503, detail="LLM API Key 未配置，请在 .env 中设置 LLM_API_KEY")

    # 1. 知识检索
    rag_chunks = retrieve(req.message, course=req.course, top_k=5)
    rag_context = _build_rag_context(rag_chunks)

    # 2. 构造消息
    system_prompt = get_system_prompt()
    user_message = _construct_chat_message(req.message, req.mode, req.course, rag_context)

    # 3. 调用 LLM
    raw_answer = llm.chat(user_message, system_prompt=system_prompt, history=req.history)

    # 4. 物理校验 + 修订
    if settings.VALIDATOR_ENABLED:
        final_answer, warnings = validate_and_rewrite(
            raw_answer, req.message, req.mode,
            llm, pl,
            max_retries=settings.VALIDATOR_MAX_RETRIES,
        )
    else:
        final_answer = raw_answer
        warnings = []

    # 5. 解析结构化回答
    sections = _parse_structured_json(final_answer)

    return ChatResponse(
        raw_answer=final_answer,
        sections=sections,
        warnings=warnings,
        retrieved_chunks=[
            {"content": c["content"][:200], "source": c["source"], "score": c["score"]}
            for c in rag_chunks
        ],
    )


@app.post("/api/solve", response_model=SolveResponse)
async def solve(req: SolveRequest):
    """分步解题"""
    llm = get_llm_client()
    if not llm.is_configured():
        raise HTTPException(status_code=503, detail="LLM API Key 未配置")

    # 1. 知识检索
    rag_chunks = retrieve(req.problem, course=req.course, top_k=5)
    rag_context = _build_rag_context(rag_chunks)

    # 2. 构造提示
    system_prompt = get_solver_prompt()
    mode_instruction = ""
    if req.mode == "guided":
        mode_instruction = (
            "\n\n【重要】当前为引导解题模式。请不要直接给出完整答案。"
            "先分析学生卡在哪一步，给出第一级提示，等学生回应后再给下一步提示。"
            "如果学生反复不会，最多给到第二级提示后才给完整解析。"
        )

    user_message = f"""题目：{req.problem}

请按照解题流程回答：
1. 判断题型
2. 提取已知量
3. 明确未知量
4. 选择坐标系
5. 建立物理模型
6. 写出适用方程
7. 分步推导
8. 检查单位和极限情况
9. 给出最终答案
10. 总结解题方法
11. 指出常见错误

{rag_context}
{mode_instruction}"""

    raw_answer = llm.chat(user_message, system_prompt=system_prompt, history=req.history)

    # 校验
    if settings.VALIDATOR_ENABLED:
        final_answer, warnings = validate_and_rewrite(
            raw_answer, req.problem, "solve",
            llm, pl,
        )
    else:
        final_answer = raw_answer
        warnings = []

    # 提取结构化信息
    problem_type = ""
    knowns: list[str] = []
    unknowns: list[str] = []
    final_answer_str = ""
    unit_check = ""
    common_mistake = ""
    hints: list[str] = []

    for line in final_answer.split("\n"):
        line_stripped = line.strip()
        if "题型" in line_stripped and problem_type == "":
            problem_type = re.sub(r"^.*?题型[：:]\s*", "", line_stripped).strip("- *")
        elif "已知" in line_stripped:
            val = re.sub(r"^.*?已知[量]?[：:]\s*", "", line_stripped).strip("- *")
            if val:
                knowns.append(val)
        elif "未知" in line_stripped:
            val = re.sub(r"^.*?未知[量]?[：:]\s*", "", line_stripped).strip("- *")
            if val:
                unknowns.append(val)
        elif "最终答案" in line_stripped or "答案" in line_stripped:
            final_answer_str = re.sub(r"^.*?(?:最终)?答案[：:]\s*", "", line_stripped).strip("- *")
        elif "单位" in line_stripped or "量纲" in line_stripped:
            unit_check = line_stripped.strip("- *")
        elif "常见错误" in line_stripped or "误区" in line_stripped:
            common_mistake = line_stripped.strip("- *")
        elif "提示" in line_stripped and req.mode == "guided":
            val = re.sub(r"^.*?提示[：:]\s*", "", line_stripped).strip("- *")
            if val:
                hints.append(val)

    return SolveResponse(
        problem_type=problem_type,
        knowns=knowns,
        unknowns=unknowns,
        solution=final_answer,
        final_answer=final_answer_str,
        unit_check=unit_check,
        common_mistake=common_mistake,
        warnings=warnings,
        hints=hints if hints else None,
    )


@app.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(req: DiagnoseRequest):
    """误区诊断"""
    llm = get_llm_client()
    if not llm.is_configured():
        raise HTTPException(status_code=503, detail="LLM API Key 未配置")

    system_prompt = get_diagnose_prompt()

    context_str = f"\n原问题上下文：{req.question_context}" if req.question_context else ""
    user_message = f"""学生的回答：
{req.student_answer}
{context_str}

课程：{req.course or '未指定'}

请诊断这个回答中是否存在物理概念错误。"""

    raw_answer = llm.chat(user_message, system_prompt=system_prompt)

    # 解析结构化输出
    judgement = ""
    issue = ""
    correct = ""
    why = ""
    fix = ""
    follow_up = None

    current_section = ""
    for line in raw_answer.split("\n"):
        line_s = line.strip()
        if "判断" in line_s:
            current_section = "judgement"
            val = re.sub(r"^.*?判断[：:]\s*", "", line_s).strip("- *")
            if val:
                judgement = val
        elif "问题所在" in line_s:
            current_section = "issue"
        elif "正确说法" in line_s:
            current_section = "correct"
        elif "为什么会错" in line_s:
            current_section = "why"
        elif "如何修正" in line_s:
            current_section = "fix"
        elif "追问" in line_s:
            current_section = "follow_up"
            val = re.sub(r"^.*?追问[：:]\s*", "", line_s).strip("- *")
            if val:
                follow_up = val
        elif line_s and not line_s.startswith("#"):
            if current_section == "judgement" and not judgement:
                judgement = line_s.strip("- *")
            elif current_section == "issue":
                issue += line_s + "\n"
            elif current_section == "correct":
                correct += line_s + "\n"
            elif current_section == "why":
                why += line_s + "\n"
            elif current_section == "fix":
                fix += line_s + "\n"
            elif current_section == "follow_up" and not follow_up:
                follow_up = line_s.strip("- *")

    return DiagnoseResponse(
        judgement=judgement or "无法判断",
        issue=issue.strip(),
        correct_explanation=correct.strip(),
        why_wrong=why.strip(),
        how_to_fix=fix.strip(),
        follow_up_question=follow_up,
    )


@app.post("/api/exercise", response_model=ExerciseResponse)
async def generate_exercise(req: ExerciseRequest):
    """生成练习题"""
    llm = get_llm_client()
    if not llm.is_configured():
        raise HTTPException(status_code=503, detail="LLM API Key 未配置")

    system_prompt = get_exercise_prompt()

    # 检索相关知识
    rag_chunks = retrieve(req.topic, course=req.course, top_k=3)
    rag_context = _build_rag_context(rag_chunks)

    user_message = f"""请生成 {req.count} 道关于「{req.topic}」的练习题。

难度：{req.difficulty}
课程：{req.course or '未指定'}

{rag_context}

请以 JSON 格式输出，格式如下：
```json
[
  {{
    "question": "题目描述",
    "answer": "答案",
    "solution": "详细解答",
    "difficulty": "{req.difficulty}"
  }}
]
```"""

    raw_answer = llm.chat_json(user_message, system_prompt=system_prompt)

    # 解析 JSON
    try:
        # 去掉可能的 markdown 代码块
        json_str = re.sub(r"```json\s*|```\s*", "", raw_answer).strip()
        data = json.loads(json_str)
        exercises = [ExerciseItem(**item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        # fallback: 返回原始回答作为一道题
        exercises = [ExerciseItem(
            question=req.topic,
            answer="",
            solution=raw_answer,
            difficulty=req.difficulty,
        )]

    return ExerciseResponse(exercises=exercises)


@app.post("/api/retrieve", response_model=RetrieveResponse)
async def retrieve_knowledge(req: RetrieveRequest):
    """知识库检索"""
    chunks = retrieve(req.query, course=req.course, top_k=req.top_k)
    return RetrieveResponse(
        chunks=[RetrieveChunk(**c) for c in chunks]
    )


@app.get("/api/knowledge/stats")
async def knowledge_stats():
    """知识库统计"""
    try:
        stats = get_collection_stats()
        return {"status": "ok", **stats}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/knowledge/reload")
async def reload_knowledge():
    """重新构建知识库索引"""
    try:
        n = build_index(force=True)
        return {"status": "ok", "chunks_indexed": n}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 入口 ──────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)
