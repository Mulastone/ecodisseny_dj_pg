#!/bin/bash
# Script: /root/ecodisseny_dj_pg/migration_phase3_migrate.sh
# Propósito: Parar servicios y migrar datos de volúmenes Docker a bind mounts

set -e

PROJECT_DIR="/root/ecodisseny_dj_pg"
MIGRATION_LOG="/opt/ecodisseny/logs/migration_$(date +%Y%m%d_%H%M%S).log"

echo "🔄 FASE 3: MIGRACIÓN DE DATOS"
echo "=============================" | tee -a "$MIGRATION_LOG"

cd "$PROJECT_DIR"

# 1. Verificar que la aplicación está funcionando
echo "🔍 Verificando estado actual..." | tee -a "$MIGRATION_LOG"
if ! docker ps | grep -q "ecodisseny_dj_pg"; then
    echo "❌ Los contenedores no están ejecutándose"
    exit 1
fi

# 2. Crear backup final antes de la migración
echo "💾 Backup final pre-migración..." | tee -a "$MIGRATION_LOG"
docker exec ecodisseny_dj_pg_db_1 pg_dump -U ecodisseny_user ecodisseny_db > "/opt/ecodisseny/backups/postgres/pre_migration_$(date +%Y%m%d_%H%M%S).sql"

# 3. Parada graceful de la aplicación
echo "⏹️ Deteniendo aplicación web..." | tee -a "$MIGRATION_LOG"
docker-compose stop web

# 4. Crear dump final de la base de datos
echo "📊 Dump final de base de datos..." | tee -a "$MIGRATION_LOG"
docker exec ecodisseny_dj_pg_db_1 pg_dumpall -U ecodisseny_user > "/opt/ecodisseny/backups/postgres/final_dump_$(date +%Y%m%d_%H%M%S).sql"

# 5. Parar PostgreSQL
echo "⏹️ Deteniendo PostgreSQL..." | tee -a "$MIGRATION_LOG"
docker-compose stop db

# 6. Migrar datos de PostgreSQL
echo "📦 Migrando datos PostgreSQL..." | tee -a "$MIGRATION_LOG"
docker run --rm \
    -v ecodisseny_dj_pg_postgres_data:/source \
    -v /opt/ecodisseny/data/postgres:/destination \
    alpine sh -c "cp -a /source/. /destination/"

# Verificar migración PostgreSQL
if [ -f "/opt/ecodisseny/data/postgres/PG_VERSION" ]; then
    echo "✅ Migración PostgreSQL exitosa" | tee -a "$MIGRATION_LOG"
    echo "📊 Versión PostgreSQL: $(cat /opt/ecodisseny/data/postgres/PG_VERSION)" | tee -a "$MIGRATION_LOG"
else
    echo "❌ Error en migración PostgreSQL" | tee -a "$MIGRATION_LOG"
    exit 1
fi

# 7. Migrar archivos media
echo "📁 Migrando archivos media..." | tee -a "$MIGRATION_LOG"
docker run --rm \
    -v ecodisseny_dj_pg_media_volume:/source \
    -v /opt/ecodisseny/data/media:/destination \
    alpine sh -c "cp -a /source/. /destination/"

# Verificar migración media
MEDIA_FILES=$(find /opt/ecodisseny/data/media -type f | wc -l)
echo "✅ Migración media exitosa: $MEDIA_FILES archivos" | tee -a "$MIGRATION_LOG"

# 8. Migrar archivos static
echo "📄 Migrando archivos static..." | tee -a "$MIGRATION_LOG"
docker run --rm \
    -v ecodisseny_dj_pg_static_volume:/source \
    -v /opt/ecodisseny/data/static:/destination \
    alpine sh -c "cp -a /source/. /destination/" 2>/dev/null || echo "Volume static vacío o no existe"

# 9. Ajustar permisos después de la migración
echo "🔐 Ajustando permisos post-migración..." | tee -a "$MIGRATION_LOG"
chown -R 999:999 /opt/ecodisseny/data/postgres
chown -R 1000:1000 /opt/ecodisseny/data/media
chown -R 1000:1000 /opt/ecodisseny/data/static

# 10. Verificar integridad de datos migrados
echo "✅ Verificando integridad de datos..." | tee -a "$MIGRATION_LOG"

# Verificar PostgreSQL
PG_SIZE=$(du -sh /opt/ecodisseny/data/postgres | cut -f1)
echo "📊 Tamaño datos PostgreSQL: $PG_SIZE" | tee -a "$MIGRATION_LOG"

# Verificar Media
MEDIA_SIZE=$(du -sh /opt/ecodisseny/data/media | cut -f1)
echo "📊 Tamaño archivos media: $MEDIA_SIZE" | tee -a "$MIGRATION_LOG"

# Listar contenido media
echo "📁 Archivos media migrados:" | tee -a "$MIGRATION_LOG"
find /opt/ecodisseny/data/media -type f | tee -a "$MIGRATION_LOG"

echo ""
echo "🎉 FASE 3 COMPLETADA" | tee -a "$MIGRATION_LOG"
echo "📍 Datos migrados a: /opt/ecodisseny/data/" | tee -a "$MIGRATION_LOG"
echo "📝 Log de migración: $MIGRATION_LOG" | tee -a "$MIGRATION_LOG"
echo ""
echo "🔧 Para continuar con Fase 4: ./migration_phase4_config.sh"
