import {
  ChatRequest, ChatResponse,
  SolveRequest, SolveResponse,
  DiagnoseRequest, DiagnoseResponse,
  ExerciseRequest, ExerciseResponse,
  HealthResponse,
} from './types';

const API_BASE = '';
const DEFAULT_TIMEOUT = 60000;
const HEALTH_TIMEOUT = 10000;

async function fetchWithTimeout(url: string, options: RequestInit, ms: number): Promise<Response> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  try { return await fetch(url, { ...options, signal: ctrl.signal }); }
  finally { clearTimeout(t); }
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
