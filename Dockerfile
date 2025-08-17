# Dockerfile optimizado para Ecodisseny Django + PostgreSQL
FROM python:3.12-slim as build-stage

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias de construcción
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libpq-dev \
    libglib2.0-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    libpangoft2-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio temporal para builds
WORKDIR /build

# Copiar requirements e instalar dependencias en un entorno virtual
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.12-slim as runtime-stage

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/venv/bin:$PATH"

# Instalar solo dependencias de runtime (sin herramientas de desarrollo)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    libpq5 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libpangoft2-1.0-0 \
    fontconfig \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get autoclean

# Copiar el entorno virtual desde build stage
COPY --from=build-stage /opt/venv /opt/venv

# Crear directorio de trabajo
WORKDIR /app

# Copiar código de la aplicación
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
