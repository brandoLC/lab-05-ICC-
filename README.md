# Mundial 2026 — Aplicación de Gestión de Partidos

Aplicación web completa en **arquitectura de 3 capas** para gestionar partidos del Mundial de Fútbol 2026. Permite ver el calendario oficial, registrar predicciones y consultarlas en un dashboard oscuro estilo deportivo.

## Stack técnico

| Capa | Tecnología | Imagen base |
|------|-----------|-------------|
| Presentación | React 18 + Vite | `node:20-alpine` (build) + `nginx:alpine` (runtime) |
| Lógica de negocio | FastAPI + SQLAlchemy + Requests | `python:3.12-slim` |
| Acceso a datos | PostgreSQL 15 | `postgres:15-alpine` |

**Imágenes publicadas en Docker Hub** ([brando14](https://hub.docker.com/u/brando14)):
- `brando14/mundial-backend:v1.0`
- `brando14/mundial-frontend:v1.0`

---

## 🐳 Publicar imágenes en Docker Hub

Después de hacer cambios en el código, reconstruye y sube las imágenes a tu cuenta `brando14`:

```bash
# 1) Build de imágenes
docker build -t brando14/mundial-backend:v1.0 ./backend
docker build -t brando14/mundial-frontend:v1.0 ./frontend

# 2) Login en Docker Hub
docker login
# Username: brando14
# Password: <tu-token-o-contraseña>

# 3) Push a Docker Hub
docker push brando14/mundial-backend:v1.0
docker push brando14/mundial-frontend:v1.0
```

> 💡 Si quieres publicar una nueva versión, cambia `v1.0` por `v1.1`, `v2.0`, etc.

## 📤 Subir el proyecto a GitHub

```bash
# Inicializar y subir al repositorio
git init
git add .
git commit -m "feat: lab-05 mundial app - arquitectura 3 capas con Docker"
git branch -M main
git remote add origin https://github.com/brandoLC/lab-05-ICC-.git
git push -u origin main
```

---

## 🚀 Despliegue rápido en AWS EC2 (m7i-flex.large)

### Paso 1 — Lanzar instancia EC2
- **AMI:** Amazon Linux 2023
- **Tipo:** m7i-flex.large (2 vCPU, 8GB RAM)
- **Storage:** 30GB gp3
- **Security Group:** abrir puertos **22 (SSH)**, **80 (HTTP)**, **8000 (API)**

### Paso 2 — Conectarse e instalar Docker
```bash
ssh -i tu-key.pem ec2-user@TU_IP_PUBLICA

sudo yum update -y
sudo yum install -y docker git
sudo service docker start
sudo usermod -aG docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
newgrp docker
```

### Paso 3 — Clonar y configurar
```bash
git clone https://github.com/brandoLC/lab-05-ICC-.git
cd lab-05-ICC-
cp .env.example .env
nano .env
# Cambiar solo:
#   POSTGRES_PASSWORD=<contraseña-segura>
#   VITE_API_URL=http://TU_IP_EC2:8000
# El FOOTBALL_API_TOKEN ya viene configurado
```

### Paso 4 — Desplegar desde Docker Hub
```bash
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

> El `docker-compose.prod.yml` está configurado con `image: brando14/mundial-*:v1.0`, así que **jala directamente** las imágenes de Docker Hub sin necesidad de hacer build en la EC2.

### Paso 5 — Verificar
- **Frontend (dashboard):** `http://TU_IP_EC2`
- **Documentación API:** `http://TU_IP_EC2:8000/docs`
- **Health check:** `http://TU_IP_EC2:8000/health`

### 🔧 Alternativa: build local en EC2
Si modificas el código y quieres buildear localmente en la EC2 (sin re-subir a Docker Hub):
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Comandos útiles en producción
```bash
# Ver logs de un servicio específico
docker-compose -f docker-compose.prod.yml logs -f backend

# Reiniciar un servicio
docker-compose -f docker-compose.prod.yml restart backend

# Detener todo (conservando datos)
docker-compose -f docker-compose.prod.yml down

# Detener y eliminar volúmenes (⚠️ BORRA LA BD)
docker-compose -f docker-compose.prod.yml down -v

# Re-descargar la última versión de la imagen desde Docker Hub
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## 💻 Desarrollo local

### Opción A — Jalando imágenes de Docker Hub (más rápido)
```bash
cp .env.example .env
# (opcional) ajustar VITE_API_URL=http://localhost:8000

docker-compose up -d
```
- Frontend: http://localhost
- API: http://localhost:8000
- Docs interactivas: http://localhost:8000/docs

### Opción B — Build local (cuando modificas el código)
```bash
docker-compose up -d --build
```

---

## 📡 API REST

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Estado de la app y conexión a BD |
| `GET` | `/api/matches` | Lista todos los partidos del Mundial 2026 |
| `GET` | `/api/matches/{id}` | Detalle de un partido |
| `POST` | `/api/predictions` | Crea una predicción |
| `GET` | `/api/predictions` | Lista todas las predicciones con info del partido |

### Ejemplo: crear predicción
```bash
curl -X POST http://localhost:8000/api/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": 1,
    "predicted_winner": "home",
    "predicted_score_home": 2,
    "predicted_score_away": 1
  }'
```

---

## 📂 Estructura del proyecto

Ver [ARCHITECTURE.md](./ARCHITECTURE.md) para el detalle completo de capas, diagramas de flujo y esquema de base de datos.

```
mundial-app/
├── frontend/      # React + Vite + Nginx
├── backend/       # FastAPI + SQLAlchemy
├── docker-compose.yml       # Desarrollo
├── docker-compose.prod.yml  # Producción (AWS EC2)
├── .env.example
└── README.md
```

---

## ⚽ Datos del Mundial 2026

Al iniciar, el backend consulta automáticamente la API de [football-data.org](https://www.football-data.org/) y guarda los partidos en PostgreSQL. **Si la API falla**, se cargan **12 partidos reales simulados** (sedes, grupos y equipos confirmados del Mundial 2026) para que la app funcione sin conexión.

---

## 🎨 Diseño

Dashboard oscuro con acentos verde `#00ff87` y azul `#0066ff`, tipografía **Inter** y **Rajdhani**, cards con borde sutil y hover. Logos de equipos mostrados desde la URL `crest` que entrega la API. Indicadores visuales de estado (programado / en juego / finalizado) y fase del torneo (Grupos, Octavos, Cuartos, etc).
