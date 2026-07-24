/**
 * Thin fetch wrapper for the FastAPI backend. Token lives in localStorage
 * and is attached to every authenticated call.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE || 'https://codecoach-mvp.onrender.com'

function authHeaders() {
  const token = localStorage.getItem('cc_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function readError(res) {
  try {
    const data = await res.json()
    return data.detail || 'Something went wrong'
  } catch {
    return 'Something went wrong'
  }
}

export async function register(username, email, password) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) throw new Error(await readError(res))
  const data = await res.json()
  localStorage.setItem('cc_token', data.access_token)
  return data
}

export function logout() {
  localStorage.removeItem('cc_token')
}

export async function getProfile() {
  const res = await fetch(`${API_BASE}/api/user/profile`, { headers: authHeaders() })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function updateUsername(username) {
  const res = await fetch(`${API_BASE}/api/user/update-username`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ username }),
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

/**
 * Generates questions based on programming language and requested count.
 */
export async function generateQuestion(language = "python", count = 1) {
  const res = await fetch(`${API_BASE}/api/generate-question`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ language, count }),
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function reviewCodeStream(question, language, code, onChunk) {
  const res = await fetch(`${API_BASE}/api/review-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ 
      question_prompt: question, 
      language, 
      code 
    }),
  })
  
  if (!res.ok) throw new Error(await readError(res))

  const data = await res.json()
  const feedbackText = data.feedback || "Code review complete."

  if (onChunk) {
    onChunk(feedbackText, feedbackText)
  }

  return data
}