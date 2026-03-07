#!/bin/bash
# Script: /root/ecodisseny_dj_pg/migration_phase6_backup.sh
# Propósito: Configurar sistema de backup automático

set -e

echo "💾 FASE 6: CONFIGURACIÓN DE BACKUPS AUTOMÁTICOS"
echo "==============================================="

# 1. Crear script de backup completo
echo "📝 Creando script de backup completo..."
cat > /opt/ecodisseny/scripts/backup_completo.sh << 'EOF'
#!/bin/bash
# Script de backup completo para Ecodisseny Multi-App

set -e

# Configuración
BACKUP_DIR="/opt/ecodisseny/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
RETENTION_WEEKS=12
RETENTION_MONTHS=12
LOG_FILE="/opt/ecodisseny/logs/backup_$(date +%Y%m%d).log"

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🔄 Iniciando backup completo - $DATE"

# 1. BACKUP POSTGRESQL
log "📊 Backup PostgreSQL..."
docker exec ecodisseny_dj_pg_db_1 pg_dumpall -U ecodisseny_user > \
    "$BACKUP_DIR/postgres/full_backup_$DATE.sql"

# 2. BACKUP POR BASE DE DATOS
log "🔧 Backup individual databases..."
docker exec ecodisseny_dj_pg_db_1 pg_dump -U ecodisseny_user ecodisseny_db > \
    "$BACKUP_DIR/postgres/ecodisseny_$DATE.sql"

# Backup Oscar Shop si existe
if docker exec ecodisseny_dj_pg_db_1 psql -U ecodisseny_user -lqt | cut -d \| -f 1 | grep -qw oscar_shop; then
    log "🛒 Backup Oscar Shop database..."
    docker exec ecodisseny_dj_pg_db_1 pg_dump -U ecodisseny_user oscar_shop > \
        "$BACKUP_DIR/postgres/oscar_shop_$DATE.sql"
fi

# 3. BACKUP ARCHIVOS MEDIA
log "📁 Backup archivos media..."
if [ -d "/opt/ecodisseny/data/media" ] && [ "$(ls -A /opt/ecodisseny/data/media)" ]; then
    tar -czf "$BACKUP_DIR/daily/media_ecodisseny_$DATE.tar.gz" -C /opt/ecodisseny/data/media .
else
    log "⚠️ Directorio media vacío"
fi

# 4. BACKUP ARCHIVOS OSCAR MEDIA (si existe)
if [ -d "/opt/ecodisseny/data/oscar/media" ] && [ "$(ls -A /opt/ecodisseny/data/oscar/media)" ]; then
    log "🛒 Backup media Oscar Shop..."
    tar -czf "$BACKUP_DIR/daily/media_oscar_$DATE.tar.gz" -C /opt/ecodisseny/data/oscar/media .
fi

# 5. BACKUP CONFIGURACIÓN
log "⚙️ Backup configuración..."
tar -czf "$BACKUP_DIR/daily/config_$DATE.tar.gz" -C /opt/ecodisseny/config .

# 6. BACKUP CÓDIGO APLICACIÓN
log "💻 Backup código aplicación..."
tar -czf "$BACKUP_DIR/daily/app_code_$DATE.tar.gz" -C /root/ecodisseny_dj_pg \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='media' \
    --exclude='staticfiles' \
    .

# 7. LIMPIEZA DE BACKUPS ANTIGUOS
log "🧹 Limpiando backups antiguos..."

# Backups diarios (mantener 30 días)
find "$BACKUP_DIR/daily" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/postgres" -name "*backup*.sql" -mtime +$RETENTION_DAYS -delete

# Backups semanales (mantener 12 semanas)
find "$BACKUP_DIR/weekly" -name "*.tar.gz" -mtime +$((RETENTION_WEEKS * 7)) -delete

# Backups mensuales (mantener 12 meses)
find "$BACKUP_DIR/monthly" -name "*.tar.gz" -mtime +$((RETENTION_MONTHS * 30)) -delete

# 8. VERIFICACIÓN DE INTEGRIDAD
log "✅ Verificando integridad..."
for backup in "$BACKUP_DIR/postgres"/*_$DATE.sql; do
    if [ -f "$backup" ] && [ -s "$backup" ]; then
        SIZE=$(du -h "$backup" | cut -f1)
        log "✅ $(basename "$backup") - OK ($SIZE)"
    else
        log "❌ $(basename "$backup") - FALLO"
        exit 1
    fi
done

# 9. ESTADÍSTICAS DE BACKUP
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*$DATE*" | wc -l)

log "📊 Backup completado:"
log "   - Archivos creados: $BACKUP_COUNT"
log "   - Espacio total backups: $TOTAL_SIZE"
log "   - Retención: $RETENTION_DAYS días (diario), $RETENTION_WEEKS semanas (semanal), $RETENTION_MONTHS meses (mensual)"

log "🎉 Backup completo finalizado - $DATE"

# 10. NOTIFICACIÓN (si está configurado)
if command -v mail >/dev/null 2>&1 && [ -n "${BACKUP_EMAIL:-}" ]; then
    echo "Backup completado exitosamente en $(hostname) - $DATE" | \
        mail -s "✅ Backup Ecodisseny - $DATE" "$BACKUP_EMAIL"
fi
EOF

chmod +x /opt/ecodisseny/scripts/backup_completo.sh

# 2. Crear script de backup incremental
echo "📝 Creando script de backup incremental..."
cat > /opt/ecodisseny/scripts/backup_incremental.sh << 'EOF'
#!/bin/bash
# Script de backup incremental (solo base de datos)

set -e

BACKUP_DIR="/opt/ecodisseny/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/opt/ecodisseny/logs/backup_incremental.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🔄 Backup incremental - $DATE"

# Backup solo datos modificados recientemente
docker exec ecodisseny_dj_pg_db_1 pg_dump -U ecodisseny_user ecodisseny_db > \
    "$BACKUP_DIR/incremental_$DATE.sql"

# Mantener solo los últimos 24 backups incrementales
find "$BACKUP_DIR" -name "incremental_*.sql" | sort | head -n -24 | xargs rm -f

SIZE=$(du -h "$BACKUP_DIR/incremental_$DATE.sql" | cut -f1)
log "✅ Backup incremental completado ($SIZE)"
EOF

chmod +x /opt/ecodisseny/scripts/backup_incremental.sh

# 3. Crear script de backup semanal
echo "📝 Creando script de backup semanal..."
cat > /opt/ecodisseny/scripts/backup_semanal.sh << 'EOF'
#!/bin/bash
# Script de backup semanal

set -e

BACKUP_DIR="/opt/ecodisseny/backups"
DATE=$(date +%Y%m%d)
LOG_FILE="/opt/ecodisseny/logs/backup_semanal.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🗓️ Backup semanal - $DATE"

# Crear backup completo y moverlo a directorio semanal
/opt/ecodisseny/scripts/backup_completo.sh

# Copiar backup más reciente a directorio semanal
LATEST_DB=$(ls -t "$BACKUP_DIR/postgres"/full_backup_*.sql | head -1)
LATEST_MEDIA=$(ls -t "$BACKUP_DIR/daily"/media_*.tar.gz | head -1 2>/dev/null || echo "")
LATEST_CONFIG=$(ls -t "$BACKUP_DIR/daily"/config_*.tar.gz | head -1)

cp "$LATEST_DB" "$BACKUP_DIR/weekly/weekly_db_$DATE.sql"
cp "$LATEST_CONFIG" "$BACKUP_DIR/weekly/weekly_config_$DATE.tar.gz"

if [ -n "$LATEST_MEDIA" ]; then
    cp "$LATEST_MEDIA" "$BACKUP_DIR/weekly/weekly_media_$DATE.tar.gz"
fi

log "✅ Backup semanal completado"
EOF

chmod +x /opt/ecodisseny/scripts/backup_semanal.sh

# 4. Crear directorios de scripts si no existen
mkdir -p /opt/ecodisseny/scripts

# 5. Configurar crontab para backups automáticos
echo "⏰ Configurando crontab..."
CRON_FILE="/tmp/ecodisseny_cron"
cat > "$CRON_FILE" << 'EOF'
# Ecodisseny Backup Schedule
# ==========================

# Backup completo diario a las 2:00 AM
0 2 * * * /opt/ecodisseny/scripts/backup_completo.sh >> /opt/ecodisseny/logs/cron_backup.log 2>&1

# Backup incremental cada 6 horas
0 */6 * * * /opt/ecodisseny/scripts/backup_incremental.sh >> /opt/ecodisseny/logs/cron_backup.log 2>&1

# Backup semanal (domingos a las 1:00 AM)
0 1 * * 0 /opt/ecodisseny/scripts/backup_semanal.sh >> /opt/ecodisseny/logs/cron_backup.log 2>&1

# Limpieza de logs antiguos (mensual)
0 3 1 * * find /opt/ecodisseny/logs -name "*.log" -mtime +90 -delete
EOF

# Instalar crontab
crontab "$CRON_FILE"
rm "$CRON_FILE"

# 6. Crear script de restauración
echo "📝 Creando script de restauración..."
cat > /opt/ecodisseny/scripts/restore_backup.sh << 'EOF'
#!/bin/bash
# Script de restauración de backup

set -e

if [ -z "$1" ]; then
    echo "Uso: $0 <archivo_backup.sql> [nombre_db]"
    echo "Ejemplos:"
    echo "  $0 /opt/ecodisseny/backups/postgres/ecodisseny_20250821_140000.sql"
    echo "  $0 /opt/ecodisseny/backups/postgres/full_backup_20250821_140000.sql ecodisseny_db"
    exit 1
fi

BACKUP_FILE="$1"
TARGET_DB="${2:-ecodisseny_db}"
TEMP_DB="restore_temp_$(date +%s)"
LOG_FILE="/opt/ecodisseny/logs/restore_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

if [ ! -f "$BACKUP_FILE" ]; then
    log "❌ Archivo de backup no encontrado: $BACKUP_FILE"
    exit 1
fi

log "🔄 Iniciando restauración desde: $BACKUP_FILE"
log "🎯 Base de datos objetivo: $TARGET_DB"

# 1. Crear base de datos temporal para pruebas
log "🧪 Creando base de datos temporal para verificación..."
docker exec ecodisseny_dj_pg_db_1 createdb -U ecodisseny_user "$TEMP_DB"

# 2. Restaurar en DB temporal
log "📥 Restaurando en base de datos temporal..."
docker exec -i ecodisseny_dj_pg_db_1 psql -U ecodisseny_user "$TEMP_DB" < "$BACKUP_FILE"

# 3. Verificar integridad
log "✅ Verificando integridad del backup..."
TABLE_COUNT=$(docker exec ecodisseny_dj_pg_db_1 psql -U ecodisseny_user "$TEMP_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | tr -d ' ')

if [ "$TABLE_COUNT" -gt 0 ]; then
    log "✅ Backup verificado correctamente: $TABLE_COUNT tablas encontradas"
    
    # 4. Confirmar restauración
    echo "⚠️ ADVERTENCIA: Esto sobrescribirá la base de datos '$TARGET_DB'"
    echo "Tablas que se restaurarán: $TABLE_COUNT"
    read -p "¿Confirmar restauración? (y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        log "🔄 Iniciando restauración en base de datos principal..."
        
        # Parar aplicación web temporalmente
        docker-compose stop web
        
        # Backup de seguridad antes de restaurar
        SAFETY_BACKUP="/opt/ecodisseny/backups/postgres/safety_backup_$(date +%Y%m%d_%H%M%S).sql"
        docker exec ecodisseny_dj_pg_db_1 pg_dump -U ecodisseny_user "$TARGET_DB" > "$SAFETY_BACKUP"
        log "💾 Backup de seguridad creado: $SAFETY_BACKUP"
        
        # Restaurar base de datos principal
        docker exec ecodisseny_dj_pg_db_1 dropdb -U ecodisseny_user "$TARGET_DB"
        docker exec ecodisseny_dj_pg_db_1 createdb -U ecodisseny_user "$TARGET_DB"
        docker exec -i ecodisseny_dj_pg_db_1 psql -U ecodisseny_user "$TARGET_DB" < "$BACKUP_FILE"
        
        # Reiniciar aplicación
        docker-compose up -d web
        
        log "✅ Restauración completada exitosamente"
        log "🔒 Backup de seguridad disponible en: $SAFETY_BACKUP"
    else
        log "❌ Restauración cancelada por el usuario"
    fi
else
    log "❌ Error en la verificación del backup: no se encontraron tablas"
fi

# Limpiar DB temporal
docker exec ecodisseny_dj_pg_db_1 dropdb -U ecodisseny_user "$TEMP_DB"
log "🧹 Base de datos temporal eliminada"

log "📝 Log completo disponible en: $LOG_FILE"
EOF

chmod +x /opt/ecodisseny/scripts/restore_backup.sh

# 7. Crear script de monitoreo
echo "📝 Creando script de monitoreo..."
cat > /opt/ecodisseny/scripts/monitor_sistema.sh << 'EOF'
#!/bin/bash
# Script de monitoreo del sistema

ALERT_EMAIL="admin@ecodisseny.com"
LOG_FILE="/opt/ecodisseny/logs/monitor_$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🔍 Iniciando monitoreo del sistema"

# 1. Verificar espacio en disco
DISK_USAGE=$(df /opt/ecodisseny | awk 'NR==2 {print $5}' | sed 's/%//')
log "💾 Uso de disco: ${DISK_USAGE}%"

if [ "$DISK_USAGE" -gt 85 ]; then
    log "⚠️ ALERTA: Uso de disco alto (${DISK_USAGE}%)"
    if command -v mail >/dev/null 2>&1; then
        echo "Uso de disco crítico: ${DISK_USAGE}%" | mail -s "⚠️ Alerta Disco Ecodisseny" "$ALERT_EMAIL"
    fi
fi

# 2. Verificar contenedores Docker
log "🐳 Verificando contenedores..."
for container in db web redis pgadmin; do
    if docker-compose ps | grep -q "${container}.*Up"; then
        log "✅ Contenedor $container - OK"
    else
        log "❌ ALERTA: Contenedor $container no está ejecutándose"
        if command -v mail >/dev/null 2>&1; then
            echo "Contenedor $container no está funcionando" | mail -s "❌ Alerta Contenedor" "$ALERT_EMAIL"
        fi
    fi
done

# 3. Verificar conectividad base de datos
if docker exec ecodisseny_dj_pg_db_1 pg_isready -U ecodisseny_user >/dev/null 2>&1; then
    log "✅ PostgreSQL - Conectividad OK"
else
    log "❌ ALERTA: PostgreSQL no responde"
fi

# 4. Verificar aplicación web
if curl -f -s http://localhost:8000 >/dev/null; then
    log "✅ Aplicación web - OK"
else
    log "❌ ALERTA: Aplicación web no responde"
fi

# 5. Verificar último backup
LAST_BACKUP=$(ls -t /opt/ecodisseny/backups/postgres/ecodisseny_*.sql 2>/dev/null | head -1)
if [ -n "$LAST_BACKUP" ]; then
    BACKUP_AGE=$((($(date +%s) - $(stat -c %Y "$LAST_BACKUP")) / 3600))
    log "💾 Último backup: hace ${BACKUP_AGE} horas"
    
    if [ "$BACKUP_AGE" -gt 25 ]; then
        log "⚠️ ALERTA: Último backup muy antiguo (${BACKUP_AGE}h)"
    fi
else
    log "❌ ALERTA: No se encontraron backups"
fi

# 6. Verificar logs de error
ERROR_COUNT=$(grep -c "ERROR\|CRITICAL\|FATAL" /opt/ecodisseny/logs/django/*.log 2>/dev/null || echo "0")
if [ "$ERROR_COUNT" -gt 10 ]; then
    log "⚠️ ALERTA: $ERROR_COUNT errores encontrados en logs Django"
fi

log "✅ Monitoreo completado"
EOF

chmod +x /opt/ecodisseny/scripts/monitor_sistema.sh

# 8. Configurar monitoreo en crontab
CRON_MONITOR="/tmp/monitor_cron"
cat > "$CRON_MONITOR" << 'EOF'
# Monitoreo cada 15 minutos
*/15 * * * * /opt/ecodisseny/scripts/monitor_sistema.sh >> /opt/ecodisseny/logs/cron_monitor.log 2>&1
EOF

# Añadir al crontab existente
(crontab -l 2>/dev/null; cat "$CRON_MONITOR") | crontab -
rm "$CRON_MONITOR"

# 9. Crear primer backup de prueba
echo "🧪 Ejecutando primer backup de prueba..."
/opt/ecodisseny/scripts/backup_completo.sh

echo ""
echo "🎉 FASE 6 COMPLETADA"
echo "===================="
echo "✅ Scripts de backup configurados:"
echo "   - /opt/ecodisseny/scripts/backup_completo.sh"
echo "   - /opt/ecodisseny/scripts/backup_incremental.sh"
echo "   - /opt/ecodisseny/scripts/backup_semanal.sh"
echo "   - /opt/ecodisseny/scripts/restore_backup.sh"
echo "   - /opt/ecodisseny/scripts/monitor_sistema.sh"
echo ""
echo "📅 Crontab configurado:"
echo "   - Backup completo: diario 2:00 AM"
echo "   - Backup incremental: cada 6 horas"
echo "   - Backup semanal: domingos 1:00 AM"
echo "   - Monitoreo: cada 15 minutos"
echo ""
echo "📁 Backups disponibles en: /opt/ecodisseny/backups/"
echo "📝 Logs en: /opt/ecodisseny/logs/"
echo ""
echo "🔧 Para finalizar: ./migration_phase7_cleanup.sh"
