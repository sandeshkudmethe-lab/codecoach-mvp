import { useState } from 'react'
import CodeEditor from './CodeEditor.jsx'
import StreamPanel from './StreamPanel.jsx'
import { generateQuestion, reviewCodeStream } from '../api.js'

const LANGUAGES = ['python', 'java', 'c', 'cpp']

export default function Dashboard({ user }) {
  const [language, setLanguage] = useState('python')
  const [questionsPerDay, setQuestionsPerDay] = useState(user?.daily_question_count || 1)
  
  // Store array of questions and track which index is active
  const [questions, setQuestions] = useState([])
  const [activeIdx, setActiveIdx] = useState(0)

  const [code, setCode] = useState('')
  const [loadingQuestion, setLoadingQuestion] = useState(false)
  const [reviewText, setReviewText] = useState('')
  const [reviewing, setReviewing] = useState(false)
  const [error, setError] = useState('')

  async function handleGetQuestion() {
    setLoadingQuestion(true)
    setError('')
    setQuestions([])
    setActiveIdx(0)
    setReviewText('')
    setCode('')
    try {
      // ✅ FIX 1: Pass BOTH language and questionsPerDay count
      const res = await generateQuestion(language, questionsPerDay)
      
      // ✅ FIX 2: Handle Array properly
      if (Array.isArray(res) && res.length > 0) {
        setQuestions(res)
      } else if (res && typeof res === 'object') {
        setQuestions([res])
      } else {
        setError('Received an unexpected response from the server.')
      }
    } catch (e) {
      setError(e.message || 'Could not generate questions.')
    } finally {
      setLoadingQuestion(false)
    }
  }

  // Active question object
  const currentQuestion = questions[activeIdx]

  async function handleSubmit() {
    if (!currentQuestion || !code.trim()) return
    setReviewing(true)
    setReviewText('')
    setError('')
    try {
      await reviewCodeStream(currentQuestion.prompt, language, code, (_chunk, full) => setReviewText(full))
    } catch (e) {
      setError(e.message || 'Review failed. Please try again.')
    } finally {
      setReviewing(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left column: learner state + controls */}
      <div className="lg:col-span-1 space-y-4">
        <div className="rounded-lg border border-gray-200 dark:border-gray-800 p-4 bg-white dark:bg-gray-900">
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Skill level</div>
          <div className="font-semibold capitalize">{user?.skill_level || 'beginner'}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-3 mb-1">Streak</div>
          <div className="font-semibold">
            {user?.streak || 0} day{user?.streak === 1 ? '' : 's'}
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 dark:border-gray-800 p-4 bg-white dark:bg-gray-900 space-y-3">
          <div>
            <label className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm"
            >
              {LANGUAGES.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs text-gray-500 dark:text-gray-400 block mb-1">
              Questions per day
            </label>
            <select
              value={questionsPerDay}
              onChange={(e) => setQuestionsPerDay(Number(e.target.value))}
              className="w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm"
            >
              <option value={1}>1</option>
              <option value={3}>3</option>
              <option value={5}>5</option>
            </select>
          </div>

          <button
            onClick={handleGetQuestion}
            disabled={loadingQuestion}
            className="w-full rounded-md bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium py-2 transition-colors"
          >
            {loadingQuestion ? 'Generating…' : "Get today's question(s)"}
          </button>

          {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
        </div>
      </div>

      {/* Right column: active question + editor + review */}
      <div className="lg:col-span-2 space-y-4">
        {questions.length > 0 && currentQuestion ? (
          <>
            {/* Tabs if user chose more than 1 question */}
            {questions.length > 1 && (
              <div className="flex gap-2 border-b border-gray-200 dark:border-gray-800 pb-2">
                {questions.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setActiveIdx(i)
                      setCode('')
                      setReviewText('')
                    }}
                    className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                      i === activeIdx
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200'
                    }`}
                  >
                    Question {i + 1}
                  </button>
                ))}
              </div>
            )}

            <div className="rounded-lg border border-gray-200 dark:border-gray-800 p-4 bg-white dark:bg-gray-900">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wide text-indigo-600 dark:text-indigo-400">
                  {currentQuestion.difficulty}
                </span>
                <span className="text-xs text-gray-400">·</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">{currentQuestion.topic}</span>
              </div>
              <h2 className="font-semibold text-lg mb-2">{currentQuestion.title}</h2>
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">{currentQuestion.prompt}</p>
              
              {currentQuestion.example_input && (
                <div className="text-xs font-mono bg-gray-50 dark:bg-gray-800 rounded p-2 mt-2">
                  <div>input: {currentQuestion.example_input}</div>
                  <div>output: {currentQuestion.example_output}</div>
                </div>
              )}
            </div>

            <CodeEditor code={code} setCode={setCode} language={language} />

            <button
              onClick={handleSubmit}
              disabled={reviewing || !code.trim()}
              className="rounded-md bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 transition-colors"
            >
              {reviewing ? 'Reviewing…' : 'Submit for review'}
            </button>

            <StreamPanel text={reviewText} loading={reviewing} />
          </>
        ) : (
          <div className="rounded-lg border border-dashed border-gray-300 dark:border-gray-700 p-10 text-center text-gray-500 dark:text-gray-400">
            Click "Get today's question(s)" to start practicing.
          </div>
        )}
      </div>
    </div>
  )
}