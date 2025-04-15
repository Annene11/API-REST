# Dockerfile para desplegar la API FastAPI en Render.com

FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos y código
COPY ./api/ ./

# Instalar dependencias
RUN pip install --no-cache-dir fastapi uvicorn asyncpg python-dotenv

# Exponer el puerto que usará la app
EXPOSE 8000

# Comando para ejecutar la app con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
