#!/bin/bash
# Script: /root/ecodisseny_dj_pg/migration_phase2_structure.sh
# Propósito: Crear la estructura de directorios para persistencia

set -e

echo "🏗️ FASE 2: CREACIÓN DE ESTRUCTURA DE DIRECTORIOS"
echo "================================================="

# 1. Crear estructura principal
echo "📁 Creando estructura de directorios..."
mkdir -p /opt/ecodisseny/{data/{postgres,redis,media,static,oscar/{media,static},pgadmin},backups/{postgres,daily,weekly,monthly},config/{postgres,nginx,ssl},logs/{postgres,django,oscar,nginx}}

# 2. Establecer permisos correctos
echo "🔐 Configurando permisos..."

# PostgreSQL (usuario 999:999 dentro del contenedor)
chown -R 999:999 /opt/ecodisseny/data/postgres
chown -R 999:999 /opt/ecodisseny/logs/postgres

# Redis (usuario 999:999 dentro del contenedor)
chown -R 999:999 /opt/ecodisseny/data/redis

# Media y Static (usuario web del contenedor - 1000:1000)
chown -R 1000:1000 /opt/ecodisseny/data/media
chown -R 1000:1000 /opt/ecodisseny/data/static
chown -R 1000:1000 /opt/ecodisseny/data/oscar

# pgAdmin (usuario 5050:5050 dentro del contenedor)
chown -R 5050:5050 /opt/ecodisseny/data/pgadmin

# Logs Django (usuario web del contenedor)
chown -R 1000:1000 /opt/ecodisseny/logs/django
chown -R 1000:1000 /opt/ecodisseny/logs/oscar

# Backups y config (root)
chown -R root:root /opt/ecodisseny/backups
chown -R root:root /opt/ecodisseny/config

# 3. Establecer permisos de directorio
echo "📋 Configurando permisos de acceso..."
chmod -R 755 /opt/ecodisseny/data
chmod -R 755 /opt/ecodisseny/logs
chmod -R 700 /opt/ecodisseny/backups
chmod -R 755 /opt/ecodisseny/config

# Permisos especiales para PostgreSQL
chmod 700 /opt/ecodisseny/data/postgres

# 4. Crear archivos de log iniciales
echo "📝 Creando archivos de log..."
touch /opt/ecodisseny/logs/postgres/postgresql.log
touch /opt/ecodisseny/logs/django/django.log
touch /opt/ecodisseny/logs/oscar/oscar.log
touch /opt/ecodisseny/logs/nginx/access.log
touch /opt/ecodisseny/logs/nginx/error.log

# 5. Crear configuración inicial de PostgreSQL
echo "⚙️ Creando configuración PostgreSQL..."
cat > /opt/ecodisseny/config/postgres/postgresql.conf << 'EOF'
# Configuración PostgreSQL para Ecodisseny Multi-App
# ===================================================

# Conexiones
max_connections = 100
listen_addresses = '*'
port = 5432

# Memoria
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_statement = 'mod'
log_min_duration_statement = 1000
log_connections = on
log_disconnections = on

# Checkpoints
checkpoint_segments = 32
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Autovacuum
autovacuum = on
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50

# Locale
lc_messages = 'en_US.utf8'
lc_monetary = 'es_ES.utf8'
lc_numeric = 'es_ES.utf8'
lc_time = 'es_ES.utf8'
default_text_search_config = 'pg_catalog.spanish'
EOF

# 6. Crear configuración de backup automático
echo "💾 Creando configuración de backup..."
cat > /opt/ecodisseny/config/backup_config.conf << 'EOF'
# Configuración de Backup Automático
BACKUP_RETENTION_DAYS=30
BACKUP_RETENTION_WEEKS=12
BACKUP_RETENTION_MONTHS=12
POSTGRES_USER=ecodisseny_user
POSTGRES_DB=ecodisseny_db
EMAIL_ALERTS=admin@ecodisseny.com
EOF

# 7. Verificar estructura creada
echo "✅ Verificando estructura creada..."
tree /opt/ecodisseny/ -L 3

echo ""
echo "🎉 FASE 2 COMPLETADA"
echo "📁 Estructura creada en: /opt/ecodisseny/"
echo "📊 Espacio utilizado:"
du -sh /opt/ecodisseny/
echo ""
echo "🔧 Para continuar con Fase 3: ./migration_phase3_stop.sh"
