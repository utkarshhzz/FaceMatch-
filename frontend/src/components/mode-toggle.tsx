import { Moon, Sun } from "lucide-react"
import { useTheme } from "@/components/theme-provider"
import { useEffect, useState } from "react"

export function ModeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light")
  }

  const isDark = theme === "dark"

  return (
    <button
      onClick={toggleTheme}
      className="relative inline-flex h-12 w-24 items-center rounded-full bg-slate-200 dark:bg-slate-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 hover:scale-105 active:scale-95"
      aria-label="Toggle theme"
    >
      {/* Background Icons (hidden when overlapped by moving circle) */}
      <span className={`absolute left-2 transition-opacity duration-300 ${isDark ? 'opacity-100' : 'opacity-30'}`}>
        <Sun className="h-5 w-5 text-amber-500" />
      </span>
      <span className={`absolute right-2 transition-opacity duration-300 ${isDark ? 'opacity-30' : 'opacity-100'}`}>
        <Moon className="h-5 w-5 text-indigo-400" />
      </span>

      {/* Sliding Circle (overlaps and hides background icon) */}
      <span
        className={`relative inline-block h-10 w-10 transform rounded-full bg-white shadow-lg transition-transform duration-300 ease-in-out z-10 ${
          isDark ? 'translate-x-12' : 'translate-x-1'
        }`}
      >
        {/* Active Icon inside moving circle */}
        <span className="flex h-full w-full items-center justify-center">
          {isDark ? (
            <Moon className="h-5 w-5 text-indigo-600" />
          ) : (
            <Sun className="h-5 w-5 text-amber-500" />
          )}
        </span>
      </span>
    </button>
  )
}