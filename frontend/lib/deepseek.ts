const API_KEY = process.env.LLM_API_KEY || '';
const API_BASE = process.env.LLM_API_BASE || 'https://api.deepseek.com/v1';
const MODEL = process.env.LLM_MODEL || 'deepseek-chat';

export function isConfigured(): boolean {
  return !!API_KEY && API_KEY.length > 10;
}

export async function callLLM(
  userMessage: string,
  systemPrompt?: string,
  history?: { role: string; content: string }[],
  temperature = 0.3,
  maxTokens = 4096,
): Promise<string> {
  const messages: { role: string; content: string }[] = [];
  if (systemPrompt) messages.push({ role: 'system', content: systemPrompt });
  if (history) {
    for (const h of history) {
      if (h.role === 'user' || h.role === 'assistant') messages.push(h);
    }
  }
  messages.push({ role: 'user', content: userMessage });

  const res = await fetch(`${API_BASE}/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_KEY}` },
    body: JSON.stringify({ model: MODEL, messages, temperature, max_tokens: maxTokens }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`DeepSeek API error ${res.status}: ${err}`);
  }
  const data = await res.json();
  return data.choices?.[0]?.message?.content || '';
}
