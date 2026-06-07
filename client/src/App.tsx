import { useState } from 'react'
import RewritePage from './pages/RewritePage'
import DatabaseViewer from './pages/DatabaseViewer'
import './App.css'

function App() {
  const [page, setPage] = useState<'rewrite' | 'database'>('rewrite')

  return (
    <div className="app-container">
      {/* ── Navigation Bar ──────────────────────────────────── */}
      <nav className="app-nav">
        <button
          className={`nav-tab ${page === 'rewrite' ? 'active' : ''}`}
          onClick={() => setPage('rewrite')}
        >
          ✏️ Rewrite
        </button>
        <button
          className={`nav-tab ${page === 'database' ? 'active' : ''}`}
          onClick={() => setPage('database')}
        >
          🗄️ Database
        </button>
      </nav>

      {/* ── Page Content ────────────────────────────────────── */}
      {page === 'rewrite' && <RewritePage />}
      {page === 'database' && <DatabaseViewer />}
    </div>
  )
}

export default App
