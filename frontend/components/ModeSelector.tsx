'use client';

import { ChatMode, MODE_OPTIONS } from '@/lib/types';

interface ModeSelectorProps {
  selected: ChatMode;
  onSelect: (mode: ChatMode) => void;
}

export default function ModeSelector({ selected, onSelect }: ModeSelectorProps) {
  return (
    <div className="bg-white border-b border-gray-200 px-4 py-2 flex-shrink-0 overflow-x-auto">
      <div className="flex gap-1 max-w-4xl mx-auto">
        {MODE_OPTIONS.map((opt) => (
          <button
            key={opt.key}
            onClick={() => onSelect(opt.key)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
              selected === opt.key
                ? 'bg-primary-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title={opt.description}
          >
            <span>{opt.icon}</span>
            <span className="hidden sm:inline">{opt.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
