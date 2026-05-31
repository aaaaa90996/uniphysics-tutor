'use client';

import katex from 'katex';
import FormulaRenderer from './FormulaRenderer';
import type { StructuredSection } from '@/lib/types';

interface Props {
  sections: StructuredSection[];
  fallbackContent?: string;
}

/* ── KaTeX 块级公式（绝不容忍原始文本泄漏） ───────── */

function LatexBlock({ tex }: { tex: string }) {
  try {
    const html = katex.renderToString(tex, {
      displayMode: true,
      throwOnError: true,
      strict: false,
      trust: false,
    });
    return (
      <div
        className="overflow-x-auto py-1 text-center"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  } catch {
    return (
      <div className="rounded-lg bg-red-50 px-4 py-2 text-xs text-red-500 text-center">
        公式渲染失败
      </div>
    );
  }
}

/* ── KaTeX 行内公式 ───────────────────────────────── */

function LatexInline({ tex }: { tex: string }) {
  try {
    const html = katex.renderToString(tex, {
      displayMode: false,
      throwOnError: true,
      strict: false,
      trust: false,
    });
    return (
      <span className="inline-block align-middle mx-0.5" dangerouslySetInnerHTML={{ __html: html }} />
    );
  } catch {
    return <span className="text-red-400 italic text-xs">{tex}</span>;
  }
}

/* ── 单条公式卡片 ─────────────────────────────────── */

function FormulaCard({ section }: { section: StructuredSection }) {
  const label = section.law_name || section.title;
  const hasSymbols = section.symbols && section.symbols.length > 0;

  return (
    <div className="rounded-2xl border border-gray-100 bg-white px-5 py-4">
      {label && (
        <h3 className="text-sm font-semibold text-gray-800 mb-3">{label}</h3>
      )}

      {section.formula && (
        <div className="bg-gray-50/70 rounded-xl px-4 py-5 mb-3">
          <LatexBlock tex={section.formula} />
        </div>
      )}

      {section.explanation && (
        <p className="text-sm text-gray-500 leading-relaxed mb-3">{section.explanation}</p>
      )}

      {hasSymbols && (
        <details className="group">
          <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600 transition select-none">
            查看符号说明
          </summary>
          <div className="mt-2 overflow-x-auto rounded-lg border border-gray-100">
            <table className="min-w-full text-xs">
              <thead>
                <tr className="bg-gray-50/50">
                  <th className="text-left px-3 py-1.5 font-medium text-gray-500">符号</th>
                  <th className="text-left px-3 py-1.5 font-medium text-gray-500">含义</th>
                  <th className="text-left px-3 py-1.5 font-medium text-gray-500">单位</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {section.symbols!.map((item, i) => (
                  <tr key={i}>
                    <td className="px-3 py-1.5"><LatexInline tex={item.symbol} /></td>
                    <td className="px-3 py-1.5 text-gray-600">{item.meaning}</td>
                    <td className="px-3 py-1.5 text-gray-400">{item.unit ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}
    </div>
  );
}

/* ── 文本 Section：左侧色条 ────────────────────────── */

const BAR: Record<string, string> = {
  concepts:        'border-l-blue-400',
  physics_image:   'border-l-teal-400',
  conditions:      'border-l-amber-400',
  common_mistakes: 'border-l-red-400',
};
const ICON: Record<string, string> = {
  concepts:        '📖',
  physics_image:   '🔬',
  conditions:      '⚠️',
  common_mistakes: '❌',
};

function TextSection({ section }: { section: StructuredSection }) {
  if (!section.content && !section.title) return null;
  const bar = BAR[section.type] ?? 'border-l-gray-300';
  const icon = ICON[section.type] ?? '📌';

  return (
    <div className={`mb-3 pl-3 border-l-2 ${bar}`}>
      {section.title && (
        <div className="flex items-center gap-1.5 mb-0.5">
          <span className="text-sm">{icon}</span>
          <h4 className="text-sm font-semibold text-gray-700">{section.title}</h4>
        </div>
      )}
      {section.content && (
        <p className="text-sm text-gray-500 leading-relaxed">{section.content}</p>
      )}
    </div>
  );
}

/* ── 推导步骤 ──────────────────────────────────────── */

function DerivationSection({ section }: { section: StructuredSection }) {
  if (!section.steps || section.steps.length === 0) return null;
  return (
    <div className="mb-4 rounded-2xl border border-gray-100 bg-white px-5 py-4">
      <h3 className="text-sm font-semibold text-gray-800 mb-3">
        📐 {section.title || '分步推导'}
      </h3>
      <ol className="space-y-1.5">
        {section.steps.map((step, i) => (
          <li key={i} className="flex gap-2.5 text-sm text-gray-600 leading-relaxed">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-100 text-gray-500 text-xs font-medium flex items-center justify-center mt-px">
              {i + 1}
            </span>
            <span>{step}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

/* ── 检查理解 ──────────────────────────────────────── */

function CheckUnderstandingSection({ section }: { section: StructuredSection }) {
  if (!section.content) return null;
  return (
    <div className="mb-4 rounded-2xl border border-emerald-100 bg-emerald-50/50 px-5 py-3.5">
      <div className="flex items-center gap-1.5 mb-1">
        <span>💡</span>
        <span className="text-sm font-semibold text-emerald-700">
          {section.title || '检查理解'}
        </span>
      </div>
      <p className="text-sm text-emerald-600 leading-relaxed">{section.content}</p>
    </div>
  );
}

/* ── 主入口：分区渲染 + 公式 Grid ─────────────────── */

export default function StructuredRenderer({ sections, fallbackContent }: Props) {
  if (!sections || sections.length === 0) {
    if (fallbackContent) {
      return (
        <div className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">
          {fallbackContent.replace(/[*#$`\\]/g, '')}
        </div>
      );
    }
    return null;
  }

  // 将 sections 按类型分组：连续的 formula_block 合并为 grid 区
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < sections.length) {
    const section = sections[i];

    // 连续 formula_block → 2 列 grid
    if (section.type === 'formula_block') {
      const gridItems: StructuredSection[] = [];
      while (i < sections.length && sections[i].type === 'formula_block') {
        gridItems.push(sections[i]);
        i++;
      }
      elements.push(
        <div key={`grid-${elements.length}`} className="mb-4 grid grid-cols-1 lg:grid-cols-2 gap-3">
          {gridItems.map((s, j) => (
            <FormulaCard key={j} section={s} />
          ))}
        </div>
      );
      continue;
    }

    // 推导步骤 → 占满宽
    if (section.type === 'derivation') {
      elements.push(<DerivationSection key={i} section={section} />);
      i++;
      continue;
    }

    // 检查理解
    if (section.type === 'check_understanding') {
      elements.push(<CheckUnderstandingSection key={i} section={section} />);
      i++;
      continue;
    }

    // 文本类 section
    if (['concepts', 'physics_image', 'conditions', 'common_mistakes'].includes(section.type)) {
      elements.push(<TextSection key={i} section={section} />);
      i++;
      continue;
    }

    // fallback 及其他：用纯文本渲染（不用 Markdown 解析器）
    const content = section.content;
    if (content) {
      const clean = content.replace(/[*#$`\\]/g, '');
      elements.push(
        <div key={i} className="mb-3">
          {section.title && (
            <h4 className="text-sm font-semibold text-gray-700 mb-1">{section.title}</h4>
          )}
          <p className="text-sm text-gray-500 leading-relaxed whitespace-pre-wrap">{clean}</p>
        </div>
      );
    }
    i++;
  }

  return <div className="structured-content">{elements}</div>;
}
