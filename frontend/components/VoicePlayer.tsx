'use client';

import { useState, useCallback, useRef } from 'react';

interface VoicePlayerProps {
  text: string;
}

export default function VoicePlayer({ text }: VoicePlayerProps) {
  const [speaking, setSpeaking] = useState(false);
  const synthRef = useRef<SpeechSynthesis | null>(null);

  const speak = useCallback(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;

    const synth = window.speechSynthesis;

    if (speaking) {
      synth.cancel();
      setSpeaking(false);
      return;
    }

    // 清理纯文本（去掉 Markdown 格式和 LaTeX）
    const cleanText = text
      .replace(/\$\$?[^$]+\$\$?/g, '') // 去掉 LaTeX
      .replace(/[#*`>\[\]()]/g, '')     // 去掉 Markdown 符号
      .replace(/\n+/g, '。')            // 换行转句号
      .replace(/\s+/g, ' ')
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'zh-CN';
    utterance.rate = 0.9;  // 稍慢，适合教学
    utterance.pitch = 1.0;

    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    synthRef.current = synth;
    setSpeaking(true);
    synth.speak(utterance);
  }, [text, speaking]);

  if (!text) return null;

  return (
    <div className="border-t bg-white px-4 py-2 flex items-center gap-3 flex-shrink-0">
      <button
        onClick={speak}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition ${
          speaking
            ? 'bg-red-500 text-white hover:bg-red-600'
            : 'bg-primary-600 text-white hover:bg-primary-700'
        }`}
        title={speaking ? '停止朗读' : '朗读核心内容'}
      >
        <span>{speaking ? '⏹' : '🔊'}</span>
        <span>{speaking ? '停止' : '语音播报'}</span>
      </button>

      {speaking && (
        <div className="flex items-center gap-1">
          <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-pulse" />
          <span className="text-xs text-gray-500">正在朗读...</span>
        </div>
      )}

      <span className="text-xs text-gray-400 ml-auto">
        {text.length > 60 ? text.slice(0, 60) + '...' : text}
      </span>
    </div>
  );
}
