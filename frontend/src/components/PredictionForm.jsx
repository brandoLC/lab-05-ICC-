import { useState } from 'react';
import { createPrediction } from '../services/api.js';

const WINNER_OPTIONS = [
  { value: 'home', label: 'Local' },
  { value: 'draw', label: 'Empate' },
  { value: 'away', label: 'Visitante' },
];

const WINNER_FROM_SCORE = (h, a) => {
  if (h === a) return 'draw';
  if (h > a) return 'home';
  return 'away';
};

export default function PredictionForm({ match, onCreated }) {
  const initialHome = match.score_home ?? 0;
  const initialAway = match.score_away ?? 0;
  const [scoreHome, setScoreHome] = useState(initialHome);
  const [scoreAway, setScoreAway] = useState(initialAway);
  const [winner, setWinner] = useState(
    WINNER_FROM_SCORE(Number(initialHome) || 0, Number(initialAway) || 0)
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleScoreChange = (which, value) => {
    const n = Math.max(0, Math.min(50, Number(value) || 0));
    if (which === 'home') {
      setScoreHome(n);
      setWinner(WINNER_FROM_SCORE(n, scoreAway));
    } else {
      setScoreAway(n);
      setWinner(WINNER_FROM_SCORE(scoreHome, n));
    }
  };

  const handleWinnerClick = (value) => {
    setWinner(value);
    if (value === 'draw' && scoreHome !== scoreAway) {
      // normalize scores to match
      setScoreHome(scoreAway);
    } else if (value === 'home' && scoreHome <= scoreAway) {
      setScoreAway(Math.max(0, scoreHome - 1));
    } else if (value === 'away' && scoreAway <= scoreHome) {
      setScoreHome(Math.max(0, scoreAway - 1));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const created = await createPrediction({
        match_id: match.id,
        predicted_winner: winner,
        predicted_score_home: scoreHome,
        predicted_score_away: scoreAway,
      });
      if (onCreated) onCreated(created);
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        'No se pudo registrar la predicción.';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="prediction-form" onSubmit={handleSubmit}>
      <label>Ganador</label>
      <div className="winner-group" role="radiogroup" aria-label="Resultado predicho">
        {WINNER_OPTIONS.map((opt) => (
          <button
            type="button"
            key={opt.value}
            role="radio"
            aria-checked={winner === opt.value}
            className={`winner-btn${winner === opt.value ? ' is-selected' : ''}`}
            onClick={() => handleWinnerClick(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <label>Marcador</label>
      <div className="score-inputs">
        <div className="score-input score-input--home">
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{match.home_team}</span>
          <input
            type="number"
            min={0}
            max={50}
            value={scoreHome}
            onChange={(e) => handleScoreChange('home', e.target.value)}
            aria-label={`Goles ${match.home_team}`}
          />
        </div>
        <span className="score-sep">:</span>
        <div className="score-input score-input--away">
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{match.away_team}</span>
          <input
            type="number"
            min={0}
            max={50}
            value={scoreAway}
            onChange={(e) => handleScoreChange('away', e.target.value)}
            aria-label={`Goles ${match.away_team}`}
          />
        </div>
      </div>

      {error && (
        <div style={{ color: 'var(--accent-red)', fontSize: 12 }}>⚠ {error}</div>
      )}

      <button type="submit" className="btn btn--primary" disabled={submitting}>
        {submitting ? 'Enviando…' : 'Registrar predicción'}
      </button>
    </form>
  );
}
