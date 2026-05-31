'use client';

import { CourseModule, COURSE_OPTIONS } from '@/lib/types';

interface CourseSelectorProps {
  selected: CourseModule | undefined;
  onSelect: (course: CourseModule | undefined) => void;
}

export default function CourseSelector({ selected, onSelect }: CourseSelectorProps) {
  return (
    <div className="flex items-center gap-1">
      <span className="text-xs text-gray-500 hidden md:inline">课程：</span>
      <select
        value={selected || ''}
        onChange={(e) => onSelect(e.target.value ? (e.target.value as CourseModule) : undefined)}
        className="text-sm border border-gray-300 rounded-lg px-2 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        <option value="">全部课程</option>
        {COURSE_OPTIONS.map((opt) => (
          <option key={opt.key} value={opt.key}>
            {opt.icon} {opt.label}
          </option>
        ))}
      </select>
      {selected && (
        <button
          onClick={() => onSelect(undefined)}
          className="text-xs text-gray-400 hover:text-gray-600 ml-1"
          title="清除选择"
        >
          ✕
        </button>
      )}
    </div>
  );
}
