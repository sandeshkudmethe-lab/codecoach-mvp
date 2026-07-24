/**
 * Lightweight textarea-based code editor. No Monaco/CodeMirror dependency
 * on purpose, to keep the MVP install light — swap in a real editor later
 * without touching Dashboard.jsx's contract (code, setCode, language props).
 */
export default function CodeEditor({ code, setCode, language }) {
  function handleTab(e) {
    if (e.key === 'Tab') {
      e.preventDefault()
      const { selectionStart, selectionEnd, value } = e.target
      const next = value.slice(0, selectionStart) + '  ' + value.slice(selectionEnd)
      setCode(next)
      const target = e.target
      requestAnimationFrame(() => {
        target.selectionStart = target.selectionEnd = selectionStart + 2
      })
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-800 overflow-hidden bg-white dark:bg-gray-900">
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 dark:border-gray-800 text-xs text-gray-500 dark:text-gray-400 font-mono">
        <span>solution.{language}</span>
        <span>{language}</span>
      </div>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        onKeyDown={handleTab}
        spellCheck={false}
        placeholder="Write your solution here..."
        className="w-full min-h-[220px] p-3 font-mono text-sm bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 outline-none resize-y"
      />
    </div>
  )
}
