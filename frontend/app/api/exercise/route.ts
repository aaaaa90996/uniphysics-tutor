import { NextRequest, NextResponse } from 'next/server';
import { callLLM, isConfigured } from '@/lib/deepseek';
import { exercisePrompt } from '@/lib/prompts';

export async function POST(req: NextRequest) {
  if (!isConfigured()) return NextResponse.json({ detail: 'LLM API Key 未配置' }, { status: 503 });
  try {
    const { topic, difficulty, count, course } = await req.json();
    const userMsg = `请生成 ${count || 1} 道关于「${topic}」的练习题。难度：${difficulty}。课程：${course || '未指定'}。请以 JSON 数组格式输出，每道题包含 question, answer, solution, difficulty 字段。`;
    const raw = await callLLM(userMsg, exercisePrompt, undefined, 0.1);
    let exercises: any[];
    try {
      const json = raw.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim();
      exercises = JSON.parse(json);
      if (!Array.isArray(exercises)) exercises = [exercises];
    } catch {
      exercises = [{ question: topic, answer: '', solution: raw, difficulty: difficulty || 'medium' }];
    }
    return NextResponse.json({ exercises });
  } catch (e: any) {
    return NextResponse.json({ detail: e.message }, { status: 500 });
  }
}
