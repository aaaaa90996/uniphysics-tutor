import { NextRequest, NextResponse } from 'next/server';
import { callLLM, isConfigured } from '@/lib/deepseek';
import { systemPrompt, constructChatMessage, parseStructuredJSON } from '@/lib/prompts';

export async function POST(req: NextRequest) {
  if (!isConfigured()) return NextResponse.json({ detail: 'LLM API Key 未配置' }, { status: 503 });
  try {
    const { message, mode, course, history } = await req.json();
    const raw = await callLLM(constructChatMessage(message, mode, course), systemPrompt, history);
    return NextResponse.json({ raw_answer: raw, sections: parseStructuredJSON(raw), warnings: [], retrieved_chunks: [] });
  } catch (e: any) {
    console.error('Chat API error:', e);
    return NextResponse.json({ detail: 'Internal server error' }, { status: 500 });
  }
}
