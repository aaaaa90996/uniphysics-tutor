import { NextResponse } from 'next/server';
export async function GET() { return NextResponse.json({ status: 'ok', total_chunks: 0, name: 'uniphysics_knowledge' }); }
