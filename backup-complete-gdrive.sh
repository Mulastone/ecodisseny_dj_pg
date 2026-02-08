#!/bin/bash

# Script de backup completo: Base de Datos + PDFs a Google Drive
# Este script ejecuta ambos backups de forma coordinada

LOG_FILE="/var/log/backup-complete-gdrive.log"
SCRIPT_DIR="/home/mulastone/proyectos/ecodisseny_dj_pg"

echo "========================================" | tee -a $LOG_FILE
echo "[$(date '+%Y-%m-%d %H:%M:%S')] INICIO BACKUP COMPLETO" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE

# 1. Backup de Base de Datos
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 1/2 - Ejecutando backup de base de datos..." | tee -a $LOG_FILE
bash "${SCRIPT_DIR}/backup-db-gdrive.sh"

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Backup de base de datos completado" | tee -a $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ ERROR en backup de base de datos" | tee -a $LOG_FILE
    exit 1
fi

# 2. Backup de PDFs
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 2/2 - Ejecutando backup de PDFs..." | tee -a $LOG_FILE
bash "${SCRIPT_DIR}/backup-pdfs-gdrive.sh"

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Backup de PDFs completado" | tee -a $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ ERROR en backup de PDFs" | tee -a $LOG_FILE
    exit 1
fi

# Resumen final
echo "========================================" | tee -a $LOG_FILE
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ BACKUP COMPLETO FINALIZADO" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE

# Mostrar espacio usado en Google Drive
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Espacio usado en Google Drive:" | tee -a $LOG_FILE
rclone about gdrive: 2>/dev/null | grep -E "Total|Used|Free" | tee -a $LOG_FILE

# Enviar notificación por email (opcional - descomentar si tienes configurado mail)
# echo "Backup completo finalizado exitosamente en $(date)" | mail -s "Backup Ecodisseny OK" tu@email.com
