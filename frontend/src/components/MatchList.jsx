import { useState } from 'react';

const STAGE_LABELS = {
  GROUP_STAGE: 'Fase de grupos',
  ROUND_OF_16: 'Octavos de final',
  QUARTER_FINALS: 'Cuartos de final',
  SEMI_FINALS: 'Semifinales',
  THIRD_PLACE: 'Tercer puesto',
  FINAL: 'Final',
};

const STATUS_LABELS = {
  SCHEDULED: 'Programado',
  TIMED: 'Programado',
  IN_PLAY: 'En curso',
  PAUSED: 'Pausado',
  FINISHED: 'Finalizado',
  AWARDED: 'Adjudicado',
  POSTPONED: 'Pospuesto',
  CANCELLED: 'Cancelado',
};

const STATUS_CLASS = {
  SCHEDULED: 'status-tag--scheduled',
  TIMED: 'status-tag--scheduled',
  IN_PLAY: 'status-tag--in_play',
  PAUSED: 'status-tag--in_play',
  FINISHED: 'status-tag--finished',
  AWARDED: 'status-tag--finished',
};

function formatMatchDate(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleString('es-ES', {
      weekday: 'short',
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

function Crest({ url, name, size = 56 }) {
  const [error, setError] = useState(false);
  if (!url || error) {
    return (
      <div
        className="team-crest team-crest--placeholder"
        style={{ width: size, height: size }}
        aria-label={name}
      >
        {name?.[0] ?? '?'}
      </div>
    );
  }
  return (
    <img
      className="team-crest"
      src={url}
      alt={`Escudo de ${name}`}
      style={{ width: size, height: size }}
      onError={() => setError(true)}
    />
  );
}

function MatchCard({ match, renderActions }) {
  const stageLabel = STAGE_LABELS[match.stage] || match.stage;
  const statusLabel = STATUS_LABELS[match.status] || match.status;
  const statusClass = STATUS_CLASS[match.status] || 'status-tag--scheduled';
  const hasScore =
    match.score_home !== null &&
    match.score_away !== null &&
    match.score_home !== undefined &&
    match.score_away !== undefined;

  return (
    <article className="match-card">
      <header className="match-card__head">
        <span className="stage-tag">{stageLabel}</span>
        {match.group_name ? <span className="group-tag">Grupo {match.group_name}</span> : null}
        <span className={`status-tag ${statusClass}`}>
          {match.status === 'IN_PLAY' && <span className="pulse" />}
          {statusLabel}
        </span>
      </header>

      <div className="match-card__date">{formatMatchDate(match.match_date)}</div>

      <div className="match-card__teams">
        <div className="team">
          <Crest url={match.home_team_crest} name={match.home_team} />
          <span className="team-name">{match.home_team}</span>
        </div>

        {hasScore ? (
          <div className="score" aria-label="Resultado">
            <span>{match.score_home}</span>
            <span>:</span>
            <span>{match.score_away}</span>
          </div>
        ) : (
          <div className="score score--pending" aria-label="Pendiente">
            VS
          </div>
        )}

        <div className="team team--away">
          <Crest url={match.away_team_crest} name={match.away_team} />
          <span className="team-name">{match.away_team}</span>
        </div>
      </div>

      {renderActions && <div>{renderActions(match)}</div>}
    </article>
  );
}

export default function MatchList({ matches, renderActions }) {
  return (
    <>
      <div className="section-header">
        <h3>Calendario</h3>
        <span className="section-count">{matches.length} partidos</span>
      </div>
      <div className="match-grid">
        {matches.map((match) => (
          <MatchCard key={match.id} match={match} renderActions={renderActions} />
        ))}
      </div>
    </>
  );
}

// re-export for testing
export { MatchCard, STAGE_LABELS, STATUS_LABELS, formatMatchDate };
