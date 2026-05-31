'use client';

import FormulaRenderer from './FormulaRenderer';
import StructuredRenderer from './StructuredRenderer';
import type { StructuredSection } from '@/lib/types';

interface BlackboardProps {
  content: string;
  sections?: StructuredSection[];
}

export default function Blackboard({ content, sections }: BlackboardProps) {
  const hasSections = sections && sections.length > 0;

  if (!content && !hasSections) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        <div className="text-center p-8">
          <div className="text-5xl mb-4">📋</div>
          <p className="text-lg font-medium mb-2">板书与公式区</p>
          <p className="text-sm">
            回答中的公式推导、关键步骤和结论<br />
            将显示在这里，方便对照学习
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {/* 标题栏 */}
      <div className="sticky top-0 bg-gray-100 border-b border-gray-200 px-4 py-2 flex items-center justify-between z-10">
        <h3 className="font-semibold text-gray-700 text-sm">📋 板书区</h3>
        <span className="text-xs text-gray-400">公式推导与知识点</span>
      </div>

      {/* 板书内容 */}
      <div className="p-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          {hasSections ? (
            <StructuredRenderer sections={sections} fallbackContent={content} />
          ) : (
            <div className="markdown-content text-sm">
              <FormulaRenderer content={content} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
