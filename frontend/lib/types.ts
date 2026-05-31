// ── 模式和课程枚举 ──────────────────────────────────────

export type ChatMode = 'explain' | 'guided' | 'full' | 'diagnose' | 'exercise';

export type CourseModule =
  | 'mechanics'
  | 'electromagnetism'
  | 'oscillation'
  | 'thermodynamics'
  | 'optics';

export interface ModeOption {
  key: ChatMode;
  label: string;
  icon: string;
  description: string;
}

export interface CourseOption {
  key: CourseModule;
  label: string;
  icon: string;
}

// ── API 请求/响应类型 ───────────────────────────────────

export interface ChatRequest {
  message: string;
  mode: ChatMode;
  course?: CourseModule;
  history?: ChatMessage[];
}

export interface SymbolItem {
  symbol: string;
  meaning: string;
  unit?: string | null;
}

export interface StructuredSection {
  type: string;
  title?: string | null;
  content?: string | null;
  law_name?: string | null;
  formula?: string | null;
  symbols?: SymbolItem[];
  explanation?: string | null;
  steps?: string[];
  known?: string[];
  unknown?: string[];
}

export interface ChatResponse {
  raw_answer: string;
  sections: StructuredSection[];
  warnings: string[];
  retrieved_chunks: RetrievedChunk[];
}

export interface SolveRequest {
  problem: string;
  mode: 'full' | 'guided';
  course?: CourseModule;
  history?: ChatMessage[];
}

export interface SolveResponse {
  problem_type: string;
  knowns: string[];
  unknowns: string[];
  solution: string;
  final_answer: string;
  unit_check: string;
  common_mistake: string;
  warnings: string[];
  hints?: string[];
}

export interface DiagnoseRequest {
  student_answer: string;
  question_context?: string;
  course?: CourseModule;
}

export interface DiagnoseResponse {
  judgement: string;
  issue: string;
  correct_explanation: string;
  why_wrong: string;
  how_to_fix: string;
  follow_up_question?: string;
}

export interface ExerciseRequest {
  topic: string;
  difficulty: 'easy' | 'medium' | 'hard';
  count: number;
  course?: CourseModule;
}

export interface ExerciseItem {
  question: string;
  answer: string;
  solution: string;
  difficulty: string;
}

export interface ExerciseResponse {
  exercises: ExerciseItem[];
}

export interface RetrievedChunk {
  content: string;
  source: string;
  score: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  llm_configured: boolean;
  knowledge_base_loaded: boolean;
}

// ── 聊天消息 ────────────────────────────────────────────

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: {
    sections?: StructuredSection[];
    warnings?: string[];
    mode?: ChatMode;
  };
}

// ── 模式选项 ────────────────────────────────────────────

export const MODE_OPTIONS: ModeOption[] = [
  { key: 'explain', label: '概念讲解', icon: '📖', description: '深入讲解物理概念与原理' },
  { key: 'guided', label: '引导解题', icon: '🧭', description: '不直接给答案，引导你思考' },
  { key: 'full', label: '完整解题', icon: '✍️', description: '分步展示完整解题过程' },
  { key: 'diagnose', label: '误区诊断', icon: '🔍', description: '检查答案中的概念错误' },
  { key: 'exercise', label: '生成练习', icon: '📝', description: '根据主题生成练习题' },
];

export const COURSE_OPTIONS: CourseOption[] = [
  { key: 'mechanics', label: '力学', icon: '⚙️' },
  { key: 'electromagnetism', label: '电磁学', icon: '⚡' },
  { key: 'oscillation', label: '振动与波', icon: '🌊' },
  { key: 'thermodynamics', label: '热学', icon: '🔥' },
  { key: 'optics', label: '光学', icon: '🔬' },
];
