'use client';

import { ChatMessage } from '@/lib/types';
import FormulaRenderer from './FormulaRenderer';
import StructuredRenderer from './StructuredRenderer';

export default function ChatBox({ message }: ChatBoxProps) {
  const isUser = message.role === 'user';
  const hasSections = message.metadata?.sections && message.metadata.sections.length > 0;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-5`}>
      <div className={`${isUser ? 'max-w-[80%]' : 'max-w-[95%]'} ${isUser ? 'order-1' : ''}`}>
        {/* 头像行 */}
        <div className={`flex items-center gap-2 mb-1.5 ${isUser ? 'justify-end' : ''}`}>
          {!isUser && <span className="text-base">🎓</span>}
          <span className="text-xs text-gray-400 font-medium">
            {isUser ? '你' : 'UniPhysics Tutor'}
          </span>
          {isUser && <span className="text-base">👤</span>}
        </div>

        {/* 消息体 */}
        {isUser ? (
          <div className="bg-blue-600 text-white rounded-2xl rounded-br-md px-4 py-2.5">
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
          </div>
        ) : hasSections ? (
          <StructuredRenderer
            sections={message.metadata!.sections!}
            fallbackContent={message.content}
          />
        ) : (
          <div className="bg-gray-100 text-gray-900 rounded-2xl rounded-bl-md px-4 py-3">
            <div className="text-sm markdown-content">
              <FormulaRenderer content={message.content} />
            </div>
          </div>
        )}

        {/* 警告 */}
        {message.metadata?.warnings && message.metadata.warnings.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.metadata.warnings.map((w, i) => (
              <div key={i} className="warning-badge">⚠️ {w}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface ChatBoxProps {
  message: ChatMessage;
}
