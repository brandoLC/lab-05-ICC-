import { useState } from 'react';

const WINNER_LABELS = {
  home: 'Local',
  away: 'Visitante',
  draw: 'Empate',
};

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('es-ES', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

function CrestMini({ url, name }) {
  const [error, setError] = useState(false);
  if (!url || error) {
    return (
      <div
        className="team-crest team-crest--placeholder"
        style={{ width: 32, height: 32, fontSize: 13 }}
        aria-label={name}
      >
        {name?.[0] ?? '?'}
      </div>
    );
  }
  return (
    <img
      src={url}
      alt={name}
      style={{ width: 32, height: 32 }}
      onError={() => setError(true)}
    />
  );
}

function PredictionRow({ prediction }) {
  const match = prediction.match;
  const winnerLabel = WINNER_LABELS[prediction.predicted_winner] || prediction.predicted_winner;
  const created = formatDate(prediction.created_at);

  if (!match) {
    return (
      <div className="prediction-row">
        <div className="prediction-row__match">
          <div className="prediction-row__teams">
            <span className="team-pair">Partido #{prediction.match_id}</span>
            <span className="meta">partido eliminado</span>
          </div>
        </div>
        <div className="prediction-row__pick">
          <span className="pick-score">
            {prediction.predicted_score_home} - {prediction.predicted_score_away}
          </span>
          <span className="pick-winner">{winnerLabel}</span>
        </div>
        <div className="prediction-row__date">{created}</div>
      </div>
    );
  }

  return (
    <div className="prediction-row">
      <div className="prediction-row__match">
        <div className="crest-stack" aria-hidden="true">
          <CrestMini url={match.home_team_crest} name={match.home_team} />
          <CrestMini url={match.away_team_crest} name={match.away_team} />
        </div>
        <div className="prediction-row__teams">
          <span className="team-pair">
            {match.home_team} <span style={{ color: 'var(--text-muted)' }}>vs</span> {match.away_team}
          </span>
          <span className="meta">
            {formatDate(match.match_date)} · {match.stage?.replace(/_/g, ' ').toLowerCase()}
          </span>
        </div>
      </div>

      <div className="prediction-row__pick">
        <span className="pick-score">
          {prediction.predicted_score_home} - {prediction.predicted_score_away}
        </span>
        <span className="pick-winner">Predice · {winnerLabel}</span>
      </div>

      <div className="prediction-row__date">creada {created}</div>
    </div>
  );
}

export default function PredictionList({ predictions }) {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="empty-state">
        <span className="emoji">🎯</span>
        <h2>Sin predicciones todavía</h2>
        <p>
          Ve a la pestaña <strong>Partidos</strong> y registra tu primera predicción para que
          aparezca aquí.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="section-header">
        <h3>Historial</h3>
        <span className="section-count">{predictions.length} predicciones</span>
      </div>
      <div className="predictions-list">
        {predictions.map((p) => (
          <PredictionRow key={p.id} prediction={p} />
        ))}
      </div>
    </>
  );
}
