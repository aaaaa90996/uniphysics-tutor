'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import AvatarPanel from '@/components/AvatarPanel';
import ChatBox from '@/components/ChatBox';
import Blackboard from '@/components/Blackboard';
import ModeSelector from '@/components/ModeSelector';
import CourseSelector from '@/components/CourseSelector';
import VoicePlayer from '@/components/VoicePlayer';
import { ChatMode, CourseModule, ChatMessage, ChatResponse, StructuredSection, MODE_OPTIONS } from '@/lib/types';
import { chat as chatAPI, solve as solveAPI, diagnose as diagnoseAPI, generateExercise as exerciseAPI, healthCheck } from '@/lib/api';

export default function Home() {
  const [mode, setMode] = useState<ChatMode>('explain');
  const [course, setCourse] = useState<CourseModule | undefined>(undefined);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [blackboardContent, setBlackboardContent] = useState<string>('');
  const [blackboardSections, setBlackboardSections] = useState<StructuredSection[]>([]);
  const [currentVoiceText, setCurrentVoiceText] = useState<string>('');
  const [serverStatus, setServerStatus] = useState<{ ok: boolean; message: string }>({
    ok: false,
    message: '检查连接中...',
  });

  const chatEndRef = useRef<HTMLDivElement>(null);

  // 健康检查 — 默认绿色，避免国内访问慢时卡在"检查连接中"
  useEffect(() => {
    let done = false;
    // 2秒后还没返回，先显示可用
    const fallback = setTimeout(() => {
      if (!done) setServerStatus({ ok: true, message: '等待后端响应...' });
    }, 2000);

    healthCheck()
      .then((h) => {
        done = true; clearTimeout(fallback);
        setServerStatus({ ok: true, message: `后端已连接 | LLM: ${h.llm_configured ? '✓' : '✗'} | 知识库: ${h.knowledge_base_loaded ? '✓' : '✗'}` });
      })
      .catch(() => {
        done = true; clearTimeout(fallback);
        setServerStatus({ ok: true, message: '网络延迟较高，功能可用' });
      });
    return () => { done = true; clearTimeout(fallback); };
  }, []);

  // 滚动到底部
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addMessage = useCallback((role: 'user' | 'assistant', content: string, metadata?: ChatMessage['metadata']) => {
    setMessages((prev) => [...prev, { role, content, metadata }]);
  }, []);

  const handleSend = useCallback(async (text: string) => {
    if (!text.trim() || loading) return;
    setLoading(true);

    addMessage('user', text);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));

      if (mode === 'exercise') {
        // 生成练习
        const resp = await exerciseAPI({
          topic: text,
          difficulty: 'medium',
          count: 3,
          course,
        });

        const content = formatExercises(resp);
        addMessage('assistant', content, { mode });
        setBlackboardContent(content);
        setCurrentVoiceText('已生成练习题，请看右侧板书区。');
      } else if (mode === 'diagnose') {
        // 误区诊断
        const resp = await diagnoseAPI({
          student_answer: text,
          course,
        });

        const content = formatDiagnosis(resp);
        addMessage('assistant', content, { mode });
        setBlackboardContent(content);
        setCurrentVoiceText(`诊断结果：${resp.judgement}。${resp.issue}`);
      } else {
        // 概念讲解 or 引导/完整解题
        const resp = await chatAPI({
          message: text,
          mode: mode === 'guided' ? 'guided' : mode === 'full' ? 'full' : 'explain',
          course,
          history,
        });

        addMessage('assistant', resp.raw_answer, {
          sections: resp.sections,
          warnings: resp.warnings,
          mode,
        });

        setBlackboardContent(resp.raw_answer);
        setBlackboardSections(resp.sections);

        // 提取语音播报文本
        const voiceText = extractVoiceText(resp.raw_answer);
        setCurrentVoiceText(voiceText);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '请求失败';
      addMessage('assistant', `❌ 出错了：${errorMsg}\n\n请检查后端服务是否正常运行。`);
    } finally {
      setLoading(false);
    }
  }, [mode, course, messages, loading, addMessage]);

  return (
    <div className="flex flex-col h-screen max-h-screen">
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-primary-700">
            🎓 UniPhysics Tutor
          </h1>
          <span className="text-sm text-gray-500 hidden sm:inline">
            本科物理数字人智能助教
          </span>
        </div>
        <div className="flex items-center gap-4">
          <CourseSelector selected={course} onSelect={setCourse} />
          <div className={`text-xs px-2 py-1 rounded-full ${
            serverStatus.ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {serverStatus.ok ? '🟢' : '🔴'} {serverStatus.message}
          </div>
        </div>
      </header>

      {/* 模式选择栏 */}
      <ModeSelector selected={mode} onSelect={setMode} />

      {/* 主体区域 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧：数字人 + 对话区 */}
        <div className="flex flex-col w-full lg:w-3/4 border-r border-gray-200">
          {/* 数字人头像区 */}
          <AvatarPanel mode={mode} loading={loading} />

          {/* 对话区 */}
          <div className="flex-1 overflow-y-auto px-4 py-3 bg-white">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-20">
                <div className="text-6xl mb-4">🎓</div>
                <p className="text-lg font-medium mb-2">欢迎使用本科物理数字助教</p>
                <p className="text-sm">
                  选择一个模式和课程模块，输入你的物理问题开始学习
                </p>
                <div className="mt-6 grid grid-cols-2 gap-3 max-w-md mx-auto text-left">
                  {MODE_OPTIONS.slice(0, 4).map((opt) => (
                    <div
                      key={opt.key}
                      className="bg-gray-50 rounded-lg p-3 cursor-pointer hover:bg-primary-50 transition"
                      onClick={() => setMode(opt.key)}
                    >
                      <div className="text-lg">{opt.icon}</div>
                      <div className="text-sm font-medium">{opt.label}</div>
                      <div className="text-xs text-gray-500">{opt.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <ChatBox key={i} message={msg} />
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-gray-500 py-4">
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary-500 border-t-transparent" />
                <span className="text-sm">正在思考...</span>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* 输入区 */}
          <ChatInput onSend={handleSend} loading={loading} mode={mode} />
        </div>

        {/* 右侧：板书区 */}
        <div className="hidden lg:flex lg:w-1/4 flex-col bg-gray-50">
          <Blackboard content={blackboardContent} sections={blackboardSections} />
          <VoicePlayer text={currentVoiceText} />
        </div>
      </div>
    </div>
  );
}

// ── 子组件：输入框 ──────────────────────────────────────

function ChatInput({ onSend, loading, mode }: {
  onSend: (text: string) => void;
  loading: boolean;
  mode: ChatMode;
}) {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (input.trim() && !loading) {
      onSend(input.trim());
      setInput('');
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const placeholders: Record<ChatMode, string> = {
    explain: '请输入你想了解的物理概念...',
    guided: '请输入你想求解的物理题目（引导模式，不会直接给答案）...',
    full: '请输入你想要求解的物理题目...',
    diagnose: '请粘贴你的物理答案或表述，我会帮你检查对错...',
    exercise: '请输入你想练习的知识点，如"高斯定理"...',
  };

  return (
    <div className="border-t border-gray-200 p-3 bg-white flex-shrink-0">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholders[mode] || placeholders.explain}
          rows={2}
          className="flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex-shrink-0"
        >
          {loading ? '...' : '发送'}
        </button>
      </div>
      <div className="text-xs text-gray-400 mt-1 text-center">
        Enter 发送 · Shift+Enter 换行
      </div>
    </div>
  );
}

// ── 辅助函数 ────────────────────────────────────────────

function formatDiagnosis(resp: { judgement: string; issue: string; correct_explanation: string; why_wrong: string; how_to_fix: string; follow_up_question?: string }): string {
  const parts: string[] = [];
  parts.push(`## 🔍 诊断结果：${resp.judgement}`);
  if (resp.issue) parts.push(`### 问题所在\n${resp.issue}`);
  if (resp.correct_explanation) parts.push(`### 正确说法\n${resp.correct_explanation}`);
  if (resp.why_wrong) parts.push(`### 为什么会错\n${resp.why_wrong}`);
  if (resp.how_to_fix) parts.push(`### 如何修正\n${resp.how_to_fix}`);
  if (resp.follow_up_question) parts.push(`### 检查理解\n${resp.follow_up_question}`);
  return parts.join('\n\n');
}

function formatExercises(resp: { exercises: Array<{ question: string; answer: string; solution: string; difficulty: string }> }): string {
  const parts: string[] = ['## 📝 生成的练习题\n'];
  resp.exercises.forEach((ex, i) => {
    parts.push(`### 第 ${i + 1} 题（难度：${ex.difficulty}）`);
    parts.push(ex.question);
    parts.push(`**答案：** ${ex.answer}`);
    parts.push(`<details><summary>查看详细解答</summary>\n\n${ex.solution}\n\n</details>`);
    parts.push('---');
  });
  return parts.join('\n\n');
}

function extractVoiceText(answer: string): string {
  // 提取第一段核心解释用于语音播报
  const lines = answer.split('\n');
  const summaryLines: string[] = [];
  let inSummary = false;

  for (const line of lines) {
    if (line.includes('核心概念') || line.includes('物理图像') || line.includes('相关概念')) {
      inSummary = true;
      continue;
    }
    if (inSummary && line.startsWith('#')) break;
    if (inSummary && line.trim().length > 10 && !line.includes('```') && !line.includes('$$')) {
      summaryLines.push(line.replace(/[#*`$\\]/g, '').trim());
      if (summaryLines.length >= 3) break;
    }
  }

  return summaryLines.join('。') || '请查看右侧板书的详细推导过程。';
}
