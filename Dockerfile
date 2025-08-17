# Dockerfile para Ecodisseny Django + PostgreSQL
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para media files
RUN mkdir -p /app/media/pdfs_pressupostos

# Crear usuario no-root para ejecutar la aplicación
RUN useradd --create-home --shell /bin/bash ecodisseny && \
    chown -R ecodisseny:ecodisseny /app

USER ecodisseny

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
