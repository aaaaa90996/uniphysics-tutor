import { NextResponse } from 'next/server';
import { isConfigured } from '@/lib/deepseek';

export async function GET() {
  return NextResponse.json({ status: 'ok', version: '0.1.0', llm_configured: isConfigured(), knowledge_base_loaded: false });
}
