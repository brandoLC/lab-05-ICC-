import { useEffect, useState } from 'react';
import MatchList from '../components/MatchList.jsx';
import PredictionForm from '../components/PredictionForm.jsx';
import { fetchHealth, fetchMatches } from '../services/api.js';

export default function Home() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);
  const [toast, setToast] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [matchesRes, healthRes] = await Promise.allSettled([
        fetchMatches(),
        fetchHealth(),
      ]);
      if (matchesRes.status === 'fulfilled') {
        setMatches(matchesRes.value.matches || []);
      } else {
        setError(
          'No se pudo conectar con la API. Verifica que el backend esté corriendo.'
        );
      }
      if (healthRes.status === 'fulfilled') {
        setHealth(healthRes.value);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handlePredictionCreated = (prediction) => {
    setToast({
      type: 'success',
      message: `Predicción registrada: ${prediction.predicted_score_home} - ${prediction.predicted_score_away}`,
    });
    setTimeout(() => setToast(null), 3500);
  };

  return (
    <div>
      <section className="page-hero">
        <h2>Partidos del Mundial 2026</h2>
        <p>
          Calendario completo de la próxima Copa del Mundo. Selecciona un partido para registrar
          tu predicción. Los datos se sincronizan automáticamente desde football-data.org.
        </p>
        <div className="hero-meta">
          {health && (
            <span className="meta-pill">
              <span
                className="dot"
                style={{
                  background:
                    health.status === 'ok' ? 'var(--accent-green)' : 'var(--accent-red)',
                  boxShadow:
                    health.status === 'ok'
                      ? '0 0 8px var(--accent-green)'
                      : '0 0 8px var(--accent-red)',
                }}
              />
              API · {health.status}
            </span>
          )}
          {health && (
            <span className="meta-pill">
              <span className="dot" style={{ background: 'var(--accent-blue)' }} />
              {health.matches_in_db} partidos cargados
            </span>
          )}
          {!loading && (
            <span className="meta-pill">
              <span className="dot" />
              {matches.length} visibles
            </span>
          )}
        </div>
      </section>

      {error && (
        <div className="error-banner" role="alert">
          <span>⚠ {error}</span>
          <button type="button" onClick={load}>
            Reintentar
          </button>
        </div>
      )}

      {loading ? (
        <div className="skeleton-grid" aria-busy="true" aria-label="Cargando partidos">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : matches.length === 0 ? (
        <div className="empty-state">
          <span className="emoji">⚽</span>
          <h2>Sin partidos disponibles</h2>
          <p>
            El backend no devolvió partidos. Espera unos segundos a que se complete la
            sincronización inicial con football-data.org o revisa los logs del servicio.
          </p>
        </div>
      ) : (
        <MatchList
          matches={matches}
          renderActions={(match) => <PredictionForm match={match} onCreated={handlePredictionCreated} />}
        />
      )}

      {toast && (
        <div className={`toast${toast.type === 'error' ? ' toast--error' : ''}`} role="status">
          {toast.type === 'success' ? '✓' : '⚠'} {toast.message}
        </div>
      )}
    </div>
  );
}
