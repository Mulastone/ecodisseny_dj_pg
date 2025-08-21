#!/bin/bash
# Script: /root/ecodisseny_dj_pg/migration_phase1_backup.sh
# Propósito: Crear backup completo antes de la migración

set -e

BACKUP_DIR="/tmp/migration_backup_$(date +%Y%m%d_%H%M%S)"
PROJECT_DIR="/root/ecodisseny_dj_pg"

echo "🔄 FASE 1: BACKUP DE SEGURIDAD COMPLETO"
echo "========================================"

# 1. Crear directorio de backup
mkdir -p "$BACKUP_DIR"
echo "✅ Directorio backup creado: $BACKUP_DIR"

# 2. Backup de la base de datos
echo "📊 Creando backup de PostgreSQL..."
cd "$PROJECT_DIR"
docker exec ecodisseny_dj_pg_db_1 pg_dumpall -U ecodisseny_user > "$BACKUP_DIR/full_database.sql"
docker exec ecodisseny_dj_pg_db_1 pg_dump -U ecodisseny_user ecodisseny_db > "$BACKUP_DIR/ecodisseny_db.sql"

# 3. Backup de volúmenes Docker completos
echo "📁 Creando backup de volúmenes Docker..."
docker run --rm -v ecodisseny_dj_pg_postgres_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/postgres_volume.tar.gz -C /data .
docker run --rm -v ecodisseny_dj_pg_media_volume:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/media_volume.tar.gz -C /data .
docker run --rm -v ecodisseny_dj_pg_static_volume:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/static_volume.tar.gz -C /data .

# 4. Backup de configuración actual
echo "⚙️ Backup de configuración..."
cp docker-compose.yml "$BACKUP_DIR/docker-compose.yml.original"
cp .env "$BACKUP_DIR/.env.original"

# 5. Verificar integridad de backups
echo "✅ Verificando integridad de backups..."
for file in "$BACKUP_DIR"/*.sql; do
    if [ -s "$file" ]; then
        echo "✅ $file - OK ($(du -h "$file" | cut -f1))"
    else
        echo "❌ $file - VACÍO O ERROR"
        exit 1
    fi
done

for file in "$BACKUP_DIR"/*.tar.gz; do
    if tar -tzf "$file" >/dev/null 2>&1; then
        echo "✅ $file - OK ($(du -h "$file" | cut -f1))"
    else
        echo "❌ $file - CORRUPTO"
        exit 1
    fi
done

echo ""
echo "🎉 FASE 1 COMPLETADA"
echo "📍 Backup guardado en: $BACKUP_DIR"
echo "📊 Archivos creados:"
ls -lh "$BACKUP_DIR"
echo ""
echo "🔧 Para continuar con Fase 2: ./migration_phase2_structure.sh"
