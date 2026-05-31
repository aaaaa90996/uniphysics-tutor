import {
  ChatRequest, ChatResponse,
  SolveRequest, SolveResponse,
  DiagnoseRequest, DiagnoseResponse,
  ExerciseRequest, ExerciseResponse,
  HealthResponse,
} from './types';

const API_BASE = '';

async function fetchAPI<T>(endpoint: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error: ${res.status}`);
  }

  return res.json();
}

export async function healthCheck(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/api/health`);
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
