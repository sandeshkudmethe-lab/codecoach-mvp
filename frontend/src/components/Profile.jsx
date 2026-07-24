import { useState } from 'react'
import { updateUsername } from '../api.js'

/**
 * Requirement 5: /profile page. Username / Email / Streak / Skill Level,
 * with an "Edit Username" flow that writes through to the backend.
 */
export default function Profile({ user, onUpdate }) {
  const [editing, setEditing] = useState(false)
  const [username, setUsername] = useState(user.username)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSave() {
    setSaving(true)
    setError('')
    try {
      const updated = await updateUsername(username)
      onUpdate((prev) => ({ ...prev, ...updated }))
      setEditing(false)
    } catch (e) {
      setError(e.message || 'Could not update username.')
    } finally {
      setSaving(false)
    }
  }

  function handleCancel() {
    setEditing(false)
    setUsername(user.username)
    setError('')
  }

  return (
    <div className="max-w-xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-xl font-bold mb-6 text-gray-900 dark:text-gray-100">Your profile</h1>

      <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
        <div className="p-4 flex items-center justify-between gap-4">
          <div className="min-w-0">
            <div className="text-xs text-gray-500 dark:text-gray-400">Username</div>
            {editing ? (
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-2 py-1 text-sm w-full"
              />
            ) : (
              <div className="font-medium text-gray-900 dark:text-gray-100">{user.username}</div>
            )}
          </div>
          {editing ? (
            <div className="flex gap-2 shrink-0">
              <button
                onClick={handleSave}
                disabled={saving}
                className="text-sm rounded-md bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Save'}
              </button>
              <button
                onClick={handleCancel}
                className="text-sm rounded-md border border-gray-300 dark:border-gray-700 px-3 py-1.5 text-gray-700 dark:text-gray-200"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setEditing(true)}
              className="text-sm rounded-md border border-gray-300 dark:border-gray-700 px-3 py-1.5 shrink-0 text-gray-700 dark:text-gray-200"
            >
              Edit username
            </button>
          )}
        </div>

        {error && <div className="p-3 text-sm text-red-600 dark:text-red-400">{error}</div>}

        <div className="p-4">
          <div className="text-xs text-gray-500 dark:text-gray-400">Email</div>
          <div className="font-medium text-gray-900 dark:text-gray-100">{user.email}</div>
        </div>

        <div className="p-4">
          <div className="text-xs text-gray-500 dark:text-gray-400">Streak</div>
          <div className="font-medium text-gray-900 dark:text-gray-100">
            {user.streak} day{user.streak === 1 ? '' : 's'}
          </div>
        </div>

        <div className="p-4">
          <div className="text-xs text-gray-500 dark:text-gray-400">Skill level</div>
          <div className="font-medium capitalize text-gray-900 dark:text-gray-100">
            {user.skill_level}
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
        Your username is stored once, on your account. Leaderboard, Battle Mode, and Friends list
        (once those ship) will all read it by looking up your account ID, so a change here updates
        it everywhere automatically — there's nothing else to keep in sync.
      </p>
    </div>
  )
}
