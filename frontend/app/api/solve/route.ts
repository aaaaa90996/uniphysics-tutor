import { NextRequest, NextResponse } from 'next/server';
import { callLLM, isConfigured } from '@/lib/deepseek';
import { solverPrompt } from '@/lib/prompts';

export async function POST(req: NextRequest) {
  if (!isConfigured()) return NextResponse.json({ detail: 'LLM API Key 未配置' }, { status: 503 });
  try {
    const { problem, mode, course, history } = await req.json();
    const courseNames: Record<string, string> = { mechanics: '力学', electromagnetism: '电磁学', oscillation: '振动与波', thermodynamics: '热学', optics: '光学' };
    const modeInst = mode === 'guided' ? '\n\n【重要】引导解题模式。不要直接给答案，先给提示。' : '';
    const userMsg = `题目：${problem}${course ? '\n课程：' + (courseNames[course] || course) : ''}\n\n请按流程回答：题型判断→已知量→未知量→坐标系→物理模型→适用方程→分步推导→单位检查→最终答案→方法总结→常见错误。${modeInst}`;
    const raw = await callLLM(userMsg, solverPrompt, history);
    // 简单解析
    const extract = (label: string) => { const l = raw.split('\n').find(x => x.includes(label)); return l ? l.replace(/^.*?[：:]\s*/, '').replace(/^[-*]\s*/, '') : ''; };
    return NextResponse.json({
      problem_type: extract('题型'), knowns: [extract('已知')].filter(Boolean), unknowns: [extract('未知')].filter(Boolean),
      solution: raw, final_answer: extract('答案'), unit_check: extract('单位') || extract('量纲'),
      common_mistake: extract('常见错误') || extract('误区'), warnings: [],
    });
  } catch (e: any) {
    console.error('Solve API error:', e);
    return NextResponse.json({ detail: 'Internal server error' }, { status: 500 });
  }
}
