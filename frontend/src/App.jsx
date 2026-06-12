import { Link, NavLink, Route, Routes } from 'react-router-dom';
import Home from './pages/Home.jsx';
import Predictions from './pages/Predictions.jsx';

export default function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 64 64" width="32" height="32">
              <circle cx="32" cy="32" r="30" fill="#0a0a0f" stroke="#00ff87" strokeWidth="3" />
              <path d="M32 14 L40 28 L24 28 Z M20 32 L44 32 L40 46 L24 46 Z" fill="#00ff87" />
              <circle cx="32" cy="32" r="3" fill="#0066ff" />
            </svg>
          </span>
          <div>
            <h1 className="brand-title">MUNDIAL 2026</h1>
            <span className="brand-subtitle">FIFA World Cup · Dashboard</span>
          </div>
        </div>

        <nav className="app-nav" aria-label="Navegación principal">
          <NavLink
            to="/"
            end
            className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`}
          >
            Partidos
          </NavLink>
          <NavLink
            to="/predictions"
            className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`}
          >
            Predicciones
          </NavLink>
          <a
            className="nav-link nav-link--ghost"
            href={`${import.meta.env.VITE_API_URL || ''}/docs`}
            target="_blank"
            rel="noreferrer"
          >
            API Docs ↗
          </a>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route
            path="*"
            element={
              <div className="empty-state">
                <h2>404</h2>
                <p>Página no encontrada. <Link to="/">Volver al inicio</Link></p>
              </div>
            }
          />
        </Routes>
      </main>

      <footer className="app-footer">
        <span>⚽ Mundial 2026 · Datos vía football-data.org</span>
        <span className="footer-dot" />
        <span>Construido con React + FastAPI + PostgreSQL</span>
      </footer>
    </div>
  );
}
