import { useState } from 'react'
import RewritePage from './pages/RewritePage'
import AnalyzePage from './pages/AnalyzePage'
import AltTextPage from './pages/AltTextPage'
import DatabaseViewer from './pages/DatabaseViewer'
import './App.css'

function App() {
  const [page, setPage] = useState<'rewrite' | 'analyze' | 'alttext' | 'database'>('rewrite')

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
          className={`nav-tab ${page === 'analyze' ? 'active' : ''}`}
          onClick={() => setPage('analyze')}
        >
          📊 Analyze
        </button>
        <button
          id="alttext-tab"
          className={`nav-tab ${page === 'alttext' ? 'active' : ''}`}
          onClick={() => setPage('alttext')}
        >
          🖼️ Alt Text
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
      {page === 'analyze' && <AnalyzePage />}
      {page === 'alttext' && <AltTextPage />}
      {page === 'database' && <DatabaseViewer />}
    </div>
  )
}

export default App
