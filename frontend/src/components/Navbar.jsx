import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Moon, Sun, User, LogOut } from 'lucide-react'

/**
 * Requirement 4: theme toggle, Tailwind dark mode (class strategy),
 * preference persisted in localStorage.
 */
export default function Navbar({ user, onLogout }) {
  const [theme, setTheme] = useState(() => localStorage.getItem('cc_theme') || 'light')

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') root.classList.add('dark')
    else root.classList.remove('dark')
    localStorage.setItem('cc_theme', theme)
  }, [theme])

  return (
    <nav className="flex items-center justify-between px-4 sm:px-6 py-3 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
      <Link to="/" className="font-bold text-lg text-gray-900 dark:text-gray-100">
        CodeCoach
      </Link>
      <div className="flex items-center gap-3">
        <button
          onClick={() => setTheme((t) => (t === 'light' ? 'dark' : 'light'))}
          aria-label="Toggle theme"
          title="Toggle theme"
          className="p-2 rounded-md border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-900 transition-colors"
        >
          {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
        </button>

        {user && (
          <>
            <Link
              to="/profile"
              className="flex items-center gap-1 text-sm text-gray-700 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              <User size={16} /> {user.username}
            </Link>
            <button
              onClick={onLogout}
              aria-label="Log out"
              title="Log out"
              className="p-2 rounded-md border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-900 transition-colors"
            >
              <LogOut size={16} />
            </button>
          </>
        )}
      </div>
    </nav>
  )
}
