import React from 'react'

export default function StreamPanel({ text, loading }) {
  if (loading) {
    return (
      <div className="rounded-lg border border-indigo-200 dark:border-indigo-900/50 p-4 bg-indigo-50/50 dark:bg-indigo-950/20 text-indigo-700 dark:text-indigo-300 text-sm flex items-center gap-2">
        <span className="inline-block animate-pulse">🤖 AI Tutor is reviewing your solution…</span>
      </div>
    )
  }

  if (!text) return null

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-800 p-4 bg-white dark:bg-gray-900 shadow-sm space-y-2">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
        <span>🤖 AI Code Review</span>
      </div>
      <div className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
        {text}
      </div>
    </div>
  )
}