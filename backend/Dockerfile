FROM python:3.12-slim
WORKDIR /app

# psycopg2-binary es un wheel precompilado, no necesita gcc/libpq-dev.
# Esto reduce el tamaño de la imagen y evita OOM en Docker Desktop.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
