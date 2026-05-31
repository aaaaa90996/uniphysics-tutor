'use client';

import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';

interface FormulaRendererProps {
  content: string;
}

/**
 * 将 LaTeX 分隔符统一转换为 remark-math 可识别的 $ 和 $$ 格式
 * 处理三种情况：
 * 1. \(...\) → $...$ （行内公式）
 * 2. \[...\] → $$...$$ （行间公式）
 * 3. 已转义的 \\\(...\\\) 和 \\\[...\\\] （来自 JSON 解析后残留的双反斜杠）
 */
function normalizeLatexDelimiters(text: string): string {
  return text
    // 处理可能的双反斜杠残留 \\\( → \( → $
    .replace(/\\\\\(/g, '\\(')
    .replace(/\\\\\)/g, '\\)')
    .replace(/\\\\\[/g, '\\[')
    .replace(/\\\\\]/g, '\\]')
    // \(...\) → $...$
    .replace(/\\\(/g, '$')
    .replace(/\\\)/g, '$')
    // \[...\] → $$...$$
    .replace(/\\\[/g, '$$\n')
    .replace(/\\\]/g, '\n$$');
}

export default function FormulaRenderer({ content }: FormulaRendererProps) {
  const normalized = useMemo(() => normalizeLatexDelimiters(content), [content]);

  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath, remarkGfm]}
      rehypePlugins={[rehypeKatex]}
      components={{
        code({ node, className, children, ...props }) {
          const isInline = !className;
          if (isInline) {
            return (
              <code className="bg-gray-200 text-pink-700 px-1 py-0.5 rounded text-xs" {...props}>
                {children}
              </code>
            );
          }
          return (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
        table({ children }) {
          return (
            <div className="overflow-x-auto my-3">
              <table className="min-w-full border-collapse border border-gray-300 text-xs">
                {children}
              </table>
            </div>
          );
        },
        th({ children }) {
          return (
            <th className="bg-blue-100 text-left px-3 py-1.5 font-semibold border border-gray-300">
              {children}
            </th>
          );
        },
        td({ children }) {
          return (
            <td className="px-3 py-1.5 border border-gray-300">
              {children}
            </td>
          );
        },
        a({ href, children }) {
          return (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
              {children}
            </a>
          );
        },
      }}
    >
      {normalized}
    </ReactMarkdown>
  );
}
