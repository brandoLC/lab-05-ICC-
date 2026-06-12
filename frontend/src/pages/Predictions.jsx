import { useEffect, useState } from 'react';
import PredictionList from '../components/PredictionList.jsx';
import { fetchPredictions } from '../services/api.js';

export default function Predictions() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPredictions();
      setPredictions(data.predictions || []);
    } catch (err) {
      console.error(err);
      setError('No se pudieron cargar las predicciones.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <section className="page-hero">
        <h2>Predicciones registradas</h2>
        <p>
          Listado completo de todas las predicciones realizadas en la plataforma, con la
          información del partido asociado.
        </p>
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
        <div className="skeleton-grid" aria-busy="true" aria-label="Cargando predicciones">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : (
        <PredictionList predictions={predictions} />
      )}
    </div>
  );
}
