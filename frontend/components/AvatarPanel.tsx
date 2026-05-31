'use client';

import { ChatMode } from '@/lib/types';

interface AvatarPanelProps {
  mode: ChatMode;
  loading: boolean;
}

const AVATAR_EXPRESSIONS: Record<ChatMode, { emoji: string; label: string; color: string }> = {
  explain: { emoji: '👨‍🏫', label: '讲解中', color: 'from-blue-500 to-cyan-500' },
  guided: { emoji: '🧭', label: '引导中', color: 'from-purple-500 to-pink-500' },
  full: { emoji: '✍️', label: '解题中', color: 'from-emerald-500 to-teal-500' },
  diagnose: { emoji: '🔍', label: '诊断中', color: 'from-orange-500 to-amber-500' },
  exercise: { emoji: '📝', label: '出题中', color: 'from-indigo-500 to-violet-500' },
};

export default function AvatarPanel({ mode, loading }: AvatarPanelProps) {
  const expression = AVATAR_EXPRESSIONS[mode] || AVATAR_EXPRESSIONS.explain;

  return (
    <div className="bg-gradient-to-r from-primary-600 to-primary-800 px-4 py-4 flex items-center gap-4 flex-shrink-0">
      {/* SVG 数字人头像 */}
      <div className="relative">
        <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${expression.color} flex items-center justify-center shadow-lg ${
          loading ? 'animate-pulse' : ''
        }`}>
          <span className="text-3xl">{expression.emoji}</span>
        </div>
        {/* 状态指示器 */}
        <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full border-2 border-white ${
          loading ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'
        }`} />
      </div>

      {/* 数字人信息 */}
      <div className="text-white">
        <h2 className="font-bold text-lg">UniPhysics Tutor</h2>
        <p className="text-sm opacity-90">
          {loading ? (
            <span className="flex items-center gap-1">
              <span className="inline-block w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="inline-block w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="inline-block w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </span>
          ) : (
            `${expression.label} · 本科物理助教`
          )}
        </p>
      </div>

      {/* 装饰性 SVG 动画 - 知识粒子 */}
      <svg className="absolute right-4 top-2 w-20 h-20 opacity-20" viewBox="0 0 100 100">
        <circle cx="30" cy="20" r="3" className={loading ? 'animate-pulse' : ''} fill="white" />
        <circle cx="70" cy="30" r="4" className={loading ? 'animate-pulse' : ''} fill="white" />
        <circle cx="50" cy="60" r="2" className={loading ? 'animate-pulse' : ''} fill="white" />
        <circle cx="20" cy="70" r="3" className={loading ? 'animate-pulse' : ''} fill="white" />
        <circle cx="80" cy="65" r="2" className={loading ? 'animate-pulse' : ''} fill="white" />
        <line x1="30" y1="20" x2="50" y2="60" stroke="white" strokeWidth="0.5" opacity="0.5" />
        <line x1="70" y1="30" x2="50" y2="60" stroke="white" strokeWidth="0.5" opacity="0.5" />
        <line x1="20" y1="70" x2="50" y2="60" stroke="white" strokeWidth="0.5" opacity="0.5" />
        <line x1="80" y1="65" x2="50" y2="60" stroke="white" strokeWidth="0.5" opacity="0.5" />
      </svg>
    </div>
  );
}
