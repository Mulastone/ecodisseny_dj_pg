#!/bin/bash

# Script de backup automático de PDFs de presupuestos a Google Drive
# Usa rclone para sincronizar con Google Drive

# Configuración
SOURCE_DIR="/home/mulastone/proyectos/ecodisseny_dj_pg/media/pdfs_pressupostos"
GDRIVE_REMOTE="gdrive:ecodisseny-backups/pdfs"
LOG_FILE="/var/log/backup-pdfs-gdrive.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Crear directorio de logs si no existe
sudo mkdir -p /var/log
sudo touch $LOG_FILE
sudo chmod 666 $LOG_FILE

# Log inicio
echo "[$DATE] Iniciando backup de PDFs a Google Drive..." >> $LOG_FILE

# Verificar que el directorio fuente existe
if [ ! -d "$SOURCE_DIR" ]; then
    echo "[$DATE] ERROR: Directorio fuente no existe: $SOURCE_DIR" >> $LOG_FILE
    exit 1
fi

# Sincronizar con Google Drive
# --log-level INFO para logs detallados
# --stats 1m para ver progreso cada minuto
# --transfers 4 para subir 4 archivos en paralelo
rclone sync "$SOURCE_DIR" "$GDRIVE_REMOTE" \
    --log-level INFO \
    --log-file=$LOG_FILE \
    --transfers 4 \
    --create-empty-src-dirs

# Verificar resultado
if [ $? -eq 0 ]; then
    echo "[$DATE] ✓ Backup completado exitosamente" >> $LOG_FILE
else
    echo "[$DATE] ✗ ERROR: El backup falló" >> $LOG_FILE
    exit 1
fi

# Mostrar estadísticas
TOTAL_SIZE=$(du -sh "$SOURCE_DIR" | cut -f1)
echo "[$DATE] Tamaño total respaldado: $TOTAL_SIZE" >> $LOG_FILE
