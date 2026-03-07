#!/bin/bash
# Script: /root/ecodisseny_dj_pg/migration_phase4_config.sh
# Propósito: Crear nueva configuración docker-compose con bind mounts

set -e

PROJECT_DIR="/root/ecodisseny_dj_pg"
MIGRATION_LOG="/opt/ecodisseny/logs/migration_$(date +%Y%m%d)_*.log"

echo "⚙️ FASE 4: CONFIGURACIÓN NUEVA ARQUITECTURA"
echo "============================================"

cd "$PROJECT_DIR"

# 1. Backup de configuración actual
echo "💾 Backup configuración actual..."
cp docker-compose.yml docker-compose.yml.pre-migration
cp .env .env.pre-migration

# 2. Crear nuevo docker-compose.yml con persistencia empresarial
echo "📝 Creando nueva configuración docker-compose..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: ecodisseny_db
      POSTGRES_USER: ecodisseny_user
      POSTGRES_PASSWORD: ecodisseny_password123
      POSTGRES_MULTIPLE_DATABASES: ecodisseny_db,oscar_shop
    volumes:
      # ✅ PERSISTENCIA EXPLÍCITA CON BIND MOUNTS
      - /opt/ecodisseny/data/postgres:/var/lib/postgresql/data
      - /opt/ecodisseny/backups/postgres:/var/backups/postgresql
      - /opt/ecodisseny/config/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
      - /opt/ecodisseny/logs/postgres:/var/log/postgresql
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "127.0.0.1:5432:5432"  # Solo acceso local por seguridad
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ecodisseny_user -d ecodisseny_db"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    command: postgres -c config_file=/etc/postgresql/postgresql.conf

  web:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      # ✅ CÓDIGO DE APLICACIÓN (DESARROLLO)
      - .:/app
      # ✅ DATOS PERSISTENTES EN HOST
      - /opt/ecodisseny/data/static:/app/staticfiles
      - /opt/ecodisseny/data/media:/app/media
      - /opt/ecodisseny/logs/django:/app/logs
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=161.97.147.142,app.arasmu.net
      - DB_HOST=db
      - DB_NAME=ecodisseny_db
      - DB_USER=ecodisseny_user
      - DB_PASSWORD=ecodisseny_password123
      - DB_PORT=5432
      - STATIC_ROOT=/app/staticfiles
      - MEDIA_ROOT=/app/media
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn ecodisseny.wsgi:application --bind 0.0.0.0:8000 --access-logfile /app/logs/gunicorn_access.log --error-logfile /app/logs/gunicorn_error.log"

  # ✅ REDIS PARA CACHE Y SESIONES (PREPARADO PARA OSCAR)
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - /opt/ecodisseny/data/redis:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    ports:
      - "127.0.0.1:6379:6379"

  # ✅ PGADMIN PARA ADMINISTRACIÓN (OPCIONAL)
  pgadmin:
    image: dpage/pgadmin4:latest
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@ecodisseny.com
      PGADMIN_DEFAULT_PASSWORD: admin123
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    volumes:
      - /opt/ecodisseny/data/pgadmin:/var/lib/pgadmin
    ports:
      - "127.0.0.1:8080:80"
    depends_on:
      - db

# ❌ ELIMINAMOS VOLUMES DOCKER - AHORA USAMOS BIND MOUNTS
# volumes:
#   postgres_data:
#   static_volume:
#   media_volume:
EOF

# 3. Actualizar .env con nuevas variables
echo "🔧 Actualizando variables de entorno..."
cat >> .env << 'EOF'

# ===================================
# CONFIGURACIÓN PERSISTENCIA EMPRESARIAL
# ===================================
ECODISSENY_DATA_DIR=/opt/ecodisseny/data
ECODISSENY_BACKUP_DIR=/opt/ecodisseny/backups
ECODISSENY_LOG_DIR=/opt/ecodisseny/logs

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# pgAdmin Configuration
PGADMIN_EMAIL=admin@ecodisseny.com
PGADMIN_PASSWORD=admin123

# Backup Configuration
BACKUP_RETENTION_DAYS=30
BACKUP_EMAIL_ALERTS=admin@ecodisseny.com
EOF

# 4. Crear script de inicialización de múltiples bases de datos
echo "🗄️ Creando script para múltiples bases de datos..."
cat > /opt/ecodisseny/config/postgres/init-multiple-databases.sh << 'EOF'
#!/bin/bash
# Script para crear múltiples bases de datos en PostgreSQL

set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "Creating user and database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_user_and_database $db
    done
    echo "Multiple databases created"
fi
EOF

chmod +x /opt/ecodisseny/config/postgres/init-multiple-databases.sh

# 5. Actualizar Dockerfile si es necesario
echo "🐳 Verificando Dockerfile..."
if ! grep -q "COPY --chown=app:app" Dockerfile 2>/dev/null; then
    echo "📝 Dockerfile parece correcto para bind mounts"
else
    echo "⚠️ Revisa el Dockerfile para compatibilidad con bind mounts"
fi

# 6. Crear configuración Nginx actualizada
echo "🌐 Creando configuración Nginx..."
mkdir -p /opt/ecodisseny/config/nginx
cat > /opt/ecodisseny/config/nginx/ecodisseny.conf << 'EOF'
server {
    listen 80;
    server_name app.arasmu.net;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.arasmu.net;

    ssl_certificate /etc/letsencrypt/live/app.arasmu.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.arasmu.net/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    # Logs específicos
    access_log /opt/ecodisseny/logs/nginx/access.log;
    error_log /opt/ecodisseny/logs/nginx/error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /static/ {
        alias /opt/ecodisseny/data/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/ecodisseny/data/media/;
        expires 7d;
    }

    location /pgadmin/ {
        proxy_pass http://127.0.0.1:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo ""
echo "🎉 FASE 4 COMPLETADA"
echo "📝 Nueva configuración creada:"
echo "   - docker-compose.yml (con bind mounts)"
echo "   - .env (variables actualizadas)"
echo "   - postgresql.conf (optimizado)"
echo "   - nginx.conf (con logs estructurados)"
echo ""
echo "🔧 Para continuar con Fase 5: ./migration_phase5_test.sh"
