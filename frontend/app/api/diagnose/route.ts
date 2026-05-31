import { NextRequest, NextResponse } from 'next/server';
import { callLLM, isConfigured } from '@/lib/deepseek';
import { diagnosePrompt } from '@/lib/prompts';

export async function POST(req: NextRequest) {
  if (!isConfigured()) return NextResponse.json({ detail: 'LLM API Key 未配置' }, { status: 503 });
  try {
    const { student_answer, question_context, course } = await req.json();
    const ctx = question_context ? `\n原问题上下文：${question_context}` : '';
    const userMsg = `学生的回答：\n${student_answer}${ctx}\n${course ? `\n课程：${course}` : ''}\n\n请诊断这个回答中是否存在物理概念错误。`;
    const raw = await callLLM(userMsg, diagnosePrompt);
    // 解析
    const get = (label: string) => { const l = raw.split('\n').find(x => x.includes(label)); return l ? l.replace(/^.*?[：:]\s*/, '').replace(/^[-*#]\s*/, '').trim() : ''; };
    const parseMulti = (label: string) => {
      const lines: string[] = []; let found = false;
      for (const l of raw.split('\n')) { if (l.includes(label)) { found = true; continue; } if (found && l.trim() && !l.includes('###') && !l.includes('判断') && !l.includes('问题所在') && !l.includes('正确说法') && !l.includes('为什么会错') && !l.includes('如何修正') && !l.includes('追问')) lines.push(l.trim()); if (found && (l.includes('###') || l.includes('判断') || l.includes('问题所在') || l.includes('正确说法') || l.includes('为什么会错') || l.includes('如何修正') || l.includes('追问'))) break; }
      return lines.join('\n');
    };
    return NextResponse.json({
      judgement: get('判断') || '无法判断',
      issue: parseMulti('问题所在') || get('问题所在'),
      correct_explanation: parseMulti('正确说法') || get('正确说法'),
      why_wrong: parseMulti('为什么会错') || get('为什么会错'),
      how_to_fix: parseMulti('如何修正') || get('如何修正'),
      follow_up_question: get('追问') || undefined,
    });
  } catch (e: any) {
    console.error('Diagnose API error:', e);
    return NextResponse.json({ detail: 'Internal server error' }, { status: 500 });
  }
}
