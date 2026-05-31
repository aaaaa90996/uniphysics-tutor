import {
  ChatRequest, ChatResponse,
  SolveRequest, SolveResponse,
  DiagnoseRequest, DiagnoseResponse,
  ExerciseRequest, ExerciseResponse,
  HealthResponse,
} from './types';

const API_BASE = '';
const DEFAULT_TIMEOUT = 60000; // 60s for LLM calls
const HEALTH_TIMEOUT = 10000;  // 10s for health check

async function fetchWithTimeout(url: string, options: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(timer);
  }
}

async function fetchAPI<T>(endpoint: string, body: unknown): Promise<T> {
  const res = await fetchWithTimeout(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }, DEFAULT_TIMEOUT);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error: ${res.status}`);
  }

  return res.json();
}

export async function healthCheck(): Promise<HealthResponse> {
  const res = await fetchWithTimeout(`${API_BASE}/api/health`, {}, HEALTH_TIMEOUT);
  return res.json();
}

export async function chat(req: ChatRequest): Promise<ChatResponse> {
  return fetchAPI<ChatResponse>('/api/chat', req);
}

export async function solve(req: SolveRequest): Promise<SolveResponse> {
  return fetchAPI<SolveResponse>('/api/solve', req);
}

export async function diagnose(req: DiagnoseRequest): Promise<DiagnoseResponse> {
  return fetchAPI<DiagnoseResponse>('/api/diagnose', req);
}

export async function generateExercise(req: ExerciseRequest): Promise<ExerciseResponse> {
  return fetchAPI<ExerciseResponse>('/api/exercise', req);
}
