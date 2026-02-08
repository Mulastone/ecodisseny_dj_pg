#!/bin/bash

# Script de backup automático de Base de Datos a Google Drive
# Hace backup de PostgreSQL y lo sube a Google Drive con rotación

# Configuración
BACKUP_DIR="/tmp/backups-db"
DATE=$(date +"%Y%m%d_%H%M%S")
DATE_SIMPLE=$(date +"%Y-%m-%d")
GDRIVE_REMOTE="gdrive:ecodisseny-backups/database"
LOG_FILE="/var/log/backup-db-gdrive.log"
CONTAINER_NAME="ecodisseny_dj_pg_db_1"

# Crear directorio temporal de backups
mkdir -p $BACKUP_DIR

# Log inicio
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando backup de base de datos..." | tee -a $LOG_FILE

# Función para hacer backup de una base de datos
backup_database() {
    local db_name=$1
    local db_user=$2
    local output_file="${BACKUP_DIR}/${db_name}_${DATE}.sql"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup de ${db_name}..." | tee -a $LOG_FILE
    
    # Hacer dump de la base de datos
    docker exec $CONTAINER_NAME pg_dump -U $db_user -d $db_name > "$output_file"
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Dump de ${db_name} completado" | tee -a $LOG_FILE
        
        # Comprimir el backup
        gzip "$output_file"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Compresión completada: ${output_file}.gz" | tee -a $LOG_FILE
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ ERROR al hacer dump de ${db_name}" | tee -a $LOG_FILE
        return 1
    fi
}

# Backup de todas las bases de datos
backup_database "ecodisseny_db" "ecodisseny_user"
backup_database "properties_db" "scraper_user"

# Crear archivo tar con todos los backups
cd $BACKUP_DIR
ARCHIVE_NAME="all_databases_${DATE}.tar.gz"
tar -czf "$ARCHIVE_NAME" *.sql.gz
rm *.sql.gz

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Archivo comprimido: $ARCHIVE_NAME" | tee -a $LOG_FILE

# Subir a Google Drive
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Subiendo a Google Drive..." | tee -a $LOG_FILE

rclone copy "${BACKUP_DIR}/${ARCHIVE_NAME}" "$GDRIVE_REMOTE" \
    --log-level INFO \
    --log-file=$LOG_FILE

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Backup subido a Google Drive" | tee -a $LOG_FILE
    
    # Limpiar archivo local
    rm "${BACKUP_DIR}/${ARCHIVE_NAME}"
    
    # Mostrar tamaño
    SIZE=$(rclone size "$GDRIVE_REMOTE" --json | grep -o '"bytes":[0-9]*' | cut -d: -f2)
    SIZE_MB=$((SIZE / 1024 / 1024))
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tamaño total en Google Drive: ${SIZE_MB}MB" | tee -a $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ ERROR al subir a Google Drive" | tee -a $LOG_FILE
    exit 1
fi

# Limpieza de backups antiguos en Google Drive (mantener últimos 30 días)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Limpiando backups antiguos..." | tee -a $LOG_FILE
rclone delete "$GDRIVE_REMOTE" --min-age 30d --log-file=$LOG_FILE

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Backup de base de datos completado" | tee -a $LOG_FILE
