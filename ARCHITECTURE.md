# Arquitectura — Mundial 2026

Documento técnico de la aplicación: capas, flujo de peticiones, esquema de datos y topología Docker en AWS EC2.

---

## 1. Diagrama de capas (3-tier)

```
┌──────────────────────────────────────────────────────────────────┐
│  CAPA 1 — PRESENTACIÓN  (Frontend React + Vite + Nginx)         │
│                                                                  │
│   ┌──────────┐  ┌──────────────────┐  ┌────────────────────┐    │
│   │ Home.jsx │  │ Predictions.jsx  │  │ MatchList / Form   │    │
│   └────┬─────┘  └────────┬─────────┘  └─────────┬──────────┘    │
│        └─────────────────┼──────────────────────┘                │
│                          │  axios / fetch                        │
│                          ▼                                       │
│                  ┌──────────────────┐                             │
│                  │   services/api   │  (VITE_API_URL)            │
│                  └────────┬─────────┘                             │
└───────────────────────────┼──────────────────────────────────────┘
                            │ HTTP/JSON  (CORS)
┌───────────────────────────▼──────────────────────────────────────┐
│  CAPA 2 — LÓGICA DE NEGOCIO  (FastAPI)                           │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │  presentation/routes/  →  matches.py, predictions.py   │    │
│   │           │ (Pydantic schemas in/out)                   │    │
│   │           ▼                                             │    │
│   │  business/  →  match_service.py, prediction_service.py  │    │
│   │           │ (reglas: no duplicar, validar predicción)   │    │
│   │           ▼                                             │    │
│   │  data/repositories/  →  match_repository, prediction...  │    │
│   └───────────┼─────────────────────────────────────────────┘    │
│               │  SQLAlchemy ORM                                  │
└───────────────▼──────────────────────────────────────────────────┘
                │  PostgreSQL Wire Protocol (5432)
┌───────────────▼──────────────────────────────────────────────────┐
│  CAPA 3 — DATOS  (PostgreSQL 15)                                 │
│                                                                  │
│   Tablas: matches  ·  predictions                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Diagrama Docker en AWS EC2 (m7i-flex.large)

```
                ┌──────────────────────────────────────────┐
                │          Internet / Browser              │
                └────────────────┬─────────────────────────┘
                                 │  HTTP :80 / :8000
                ┌────────────────▼─────────────────────────┐
                │    AWS EC2 m7i-flex.large  (Amazon       │
                │    Linux 2023) — docker-compose.prod.yml │
                │                                         │
                │  ┌──────────────────────────────────┐   │
                │  │ mundial-network  (bridge)        │   │
                │  │                                  │   │
                │  │  ┌──────────────────────────┐    │   │
                │  │  │ mundial-frontend         │    │   │
                │  │  │ nginx:alpine             │    │   │
                │  │  │ mem 1g · cpu 0.5 · :80   │    │   │
                │  │  │ → static React build     │    │   │
                │  │  └────────────┬─────────────┘    │   │
                │  │               │ /api → proxy     │   │
                │  │  ┌────────────▼─────────────┐    │   │
                │  │  │ mundial-backend          │    │   │
                │  │  │ python:3.12-slim         │    │   │
                │  │  │ FastAPI + uvicorn :8000  │    │   │
                │  │  │ mem 2g · cpu 1.0         │    │   │
                │  │  └────────────┬─────────────┘    │   │
                │  │               │ SQLAlchemy        │   │
                │  │  ┌────────────▼─────────────┐    │   │
                │  │  │ mundial-postgres         │    │   │
                │  │  │ postgres:15-alpine       │    │   │
                │  │  │ mem 2g · cpu 0.5         │    │   │
                │  │  │ Volume: postgres_data    │    │   │
                │  │  └──────────────────────────┘    │   │
                │  └──────────────────────────────────┘   │
                └──────────────────────────────────────────┘
```

**Recursos asignados** (límites docker):

| Servicio   | CPU  | RAM   | Volumen persistente |
|------------|------|-------|---------------------|
| frontend   | 0.5  | 1 GB  | —                   |
| backend    | 1.0  | 2 GB  | —                   |
| postgres   | 0.5  | 2 GB  | `postgres_data`     |

Logging: `json-file`, rotación `50m × 3`.

---

## 3. Responsabilidad de cada capa

### Capa 1 — Presentación (Frontend)
- Renderizar UI, manejar estados de carga, capturar inputs del usuario.
- Consumir la API REST con `fetch` / `axios` desde `services/api.js`.
- **No** contiene lógica de negocio; solo valida formato y muestra feedback.
- Servido por `nginx:alpine` en el contenedor final (build multistage).

### Capa 2 — Lógica de negocio (Backend)
- Expone endpoints REST con FastAPI.
- **Rutas** (`presentation/routes/`): reciben HTTP, validan con **Pydantic schemas**, delegan al servicio.
- **Servicios** (`business/`): reglas de negocio:
  - Sincronización con `football-data.org` al arrancar.
  - **Idempotencia**: no duplicar partidos existentes en BD.
  - Validación de predicciones (ganador ∈ {home, away, draw}, puntajes ≥ 0).
  - Fallback a datos simulados si la API externa falla.
- **Repositorios** (`data/repositories/`): única vía de acceso a datos; encapsulan queries SQLAlchemy.
- Logging + health check.

### Capa 3 — Datos (PostgreSQL)
- Persistencia relacional: dos tablas (`matches`, `predictions`) con PK, FK e índices.
- Volumen `postgres_data` montado en `/var/lib/postgresql/data` para sobrevivir reinicios.
- Inicialización y migraciones gestionadas por SQLAlchemy al arrancar el backend.

---

## 4. Flujo completo de una petición (ejemplo: crear predicción)

```
[Browser]  usuario envía formulario de predicción
   │
   │  POST /api/predictions   { match_id, predicted_winner, ... }
   ▼
[Nginx]  sirve el bundle React (build estático) en /
   │  (las llamadas a /api pasan por el proxy al backend en :8000)
   ▼
[FastAPI router]  predictions.py  @router.post("/")
   │  1) Valida body con PredictionCreate (Pydantic)
   │  2) Llama a prediction_service.create_prediction(...)
   ▼
[prediction_service]
   │  3) Verifica reglas: match existe, winner válido, scores ≥ 0
   │  4) Llama a prediction_repository.add(...)
   ▼
[prediction_repository]
   │  5) INSERT INTO predictions (...) RETURNING *
   ▼
[PostgreSQL]  guarda fila y devuelve row
   │
   ▲  (la respuesta sube por las mismas capas)
   ▼
[Router]  serializa con PredictionRead → JSON 201
   ▼
[Browser]  setState → actualiza lista de predicciones
```

---

## 5. Esquema de la base de datos

```
┌──────────────────────────────────┐
│            matches               │
├──────────────────────────────────┤
│ id              BIGSERIAL PK     │
│ external_id     INTEGER UNIQUE   │   ← id de football-data.org
│ match_date      TIMESTAMPTZ      │
│ status          VARCHAR(32)      │   SCHEDULED / IN_PLAY / FINISHED
│ home_team       VARCHAR(120)     │
│ home_team_crest TEXT             │   URL del escudo
│ away_team       VARCHAR(120)     │
│ away_team_crest TEXT             │
│ score_home      INTEGER NULL     │
│ score_away      INTEGER NULL     │
│ stage           VARCHAR(40)      │   GROUP_STAGE / ROUND_OF_16 / ...
│ group_name      VARCHAR(8) NULL  │   'A', 'B', ...
│ created_at      TIMESTAMPTZ      │
│ updated_at      TIMESTAMPTZ      │
└──────────────┬───────────────────┘
               │  1
               │
               │  N
┌──────────────▼───────────────────┐
│          predictions             │
├──────────────────────────────────┤
│ id                       BIGSERIAL PK
│ match_id                 BIGINT FK → matches.id  ON DELETE CASCADE
│ predicted_winner         VARCHAR(8)        home / away / draw
│ predicted_score_home     INTEGER NOT NULL
│ predicted_score_away     INTEGER NOT NULL
│ created_at               TIMESTAMPTZ
└──────────────────────────────────┘
```

**Índices**:
- `matches.external_id` UNIQUE — evita duplicados al re-sincronizar.
- `predictions.match_id` — JOIN rápido con la lista de partidos.

---

## 6. CORS

- **Desarrollo** (`docker-compose.yml`): `CORS_ORIGINS=*` permite cualquier origen.
- **Producción**: `CORS_ORIGINS` se lee de la variable de entorno (recomendado: solo la IP/público de la EC2, p. ej. `http://54.123.45.67`).
