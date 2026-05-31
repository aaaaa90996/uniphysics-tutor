"""Pydantic 请求/响应模型"""

from typing import Optional
from pydantic import BaseModel, Field


# ── 枚举类型 ─────────────────────────────────────────────

CourseModule = str  # "mechanics" | "electromagnetism" | "oscillation" | "thermodynamics" | "optics"
ChatMode = str      # "explain" | "guided" | "full" | "diagnose"
Difficulty = str    # "easy" | "medium" | "hard"


# ── 请求模型 ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., description="学生的问题", min_length=1)
    mode: ChatMode = Field(default="explain", description="模式：explain/guided/full")
    course: Optional[CourseModule] = Field(default=None, description="课程模块")
    history: Optional[list[dict]] = Field(default=None, description="对话历史")


class SolveRequest(BaseModel):
    problem: str = Field(..., description="题目描述", min_length=1)
    mode: ChatMode = Field(default="full", description="full=完整解题, guided=引导解题")
    course: Optional[CourseModule] = Field(default=None, description="课程模块")
    history: Optional[list[dict]] = Field(default=None, description="对话历史")


class DiagnoseRequest(BaseModel):
    student_answer: str = Field(..., description="学生的回答", min_length=1)
    question_context: Optional[str] = Field(default=None, description="原问题上下文")
    course: Optional[CourseModule] = Field(default=None)


class ExerciseRequest(BaseModel):
    topic: str = Field(..., description="练习主题", min_length=1)
    difficulty: Difficulty = Field(default="medium")
    count: int = Field(default=3, ge=1, le=10)
    course: Optional[CourseModule] = Field(default=None)


class RetrieveRequest(BaseModel):
    query: str = Field(..., description="检索查询", min_length=1)
    course: Optional[CourseModule] = Field(default=None)
    top_k: int = Field(default=5, ge=1, le=20)


class TTSRequest(BaseModel):
    text: str = Field(..., description="要转为语音的文本", min_length=1)


# ── 结构化回答模型 ─────────────────────────────────────

class SymbolItem(BaseModel):
    symbol: str = Field(..., description="LaTeX 符号，不含 $ 分隔符")
    meaning: str = Field(..., description="物理含义")
    unit: Optional[str] = Field(default=None, description="单位")


class FormulaBlock(BaseModel):
    law_name: Optional[str] = Field(default=None, description="定律名称")
    formula: str = Field(..., description="纯 LaTeX 公式，不含 $ 或 $$")
    symbols: list[SymbolItem] = Field(default_factory=list)
    explanation: Optional[str] = Field(default=None, description="补充说明")


class StructuredSection(BaseModel):
    type: str = Field(..., description="段落类型")
    title: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    law_name: Optional[str] = Field(default=None)
    formula: Optional[str] = Field(default=None)
    symbols: list[SymbolItem] = Field(default_factory=list)
    explanation: Optional[str] = Field(default=None)
    steps: Optional[list[str]] = Field(default=None)
    known: Optional[list[str]] = Field(default=None)
    unknown: Optional[list[str]] = Field(default=None)


# ── 响应模型 ─────────────────────────────────────────────

class ChatResponse(BaseModel):
    raw_answer: str = Field(default="", description="原始 Markdown 回答（兼容旧版）")
    sections: list[StructuredSection] = Field(default_factory=list, description="结构化段落")
    warnings: list[str] = Field(default_factory=list, description="校验警告")
    retrieved_chunks: list[dict] = Field(default_factory=list, description="检索到的知识片段")


class SolveResponse(BaseModel):
    raw_answer: str = Field(default="", description="原始回答")
    sections: list[StructuredSection] = Field(default_factory=list, description="结构化段落")
    warnings: list[str] = Field(default_factory=list)


class DiagnoseResponse(BaseModel):
    judgement: str = Field(..., description="正确/部分正确/错误/条件不足")
    issue: str = Field(default="", description="问题所在")
    correct_explanation: str = Field(default="", description="正确说法")
    why_wrong: str = Field(default="", description="为什么会错")
    how_to_fix: str = Field(default="", description="如何修正")
    follow_up_question: Optional[str] = Field(default=None)


class ExerciseItem(BaseModel):
    question: str
    answer: str
    solution: str
    difficulty: Difficulty


class ExerciseResponse(BaseModel):
    exercises: list[ExerciseItem]


class RetrieveChunk(BaseModel):
    content: str
    source: str
    score: float


class RetrieveResponse(BaseModel):
    chunks: list[RetrieveChunk]


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    llm_configured: bool = False
    knowledge_base_loaded: bool = False


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
