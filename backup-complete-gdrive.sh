#!/usr/bin/env bash
set -Eeuo pipefail

# Backup completo: BBDD + PDFs.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
LOG_FILE="${LOG_FILE:-$LOG_DIR/backup-complete-gdrive.log}"

mkdir -p "$LOG_DIR"
touch "$LOG_FILE"
chmod 640 "$LOG_FILE" 2>/dev/null || true

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "========================================"
log "INICIO BACKUP COMPLETO"
log "========================================"

log "1/2 - Ejecutando backup de base de datos..."
"${SCRIPT_DIR}/backup-db-gdrive.sh"
log "OK - Backup de base de datos completado."

log "2/2 - Ejecutando backup de PDFs..."
"${SCRIPT_DIR}/backup-pdfs-gdrive.sh"
log "OK - Backup de PDFs completado."

log "========================================"
log "BACKUP COMPLETO FINALIZADO"
log "========================================"

if command -v rclone >/dev/null 2>&1; then
  log "Espacio usado en Google Drive:"
  rclone about gdrive: 2>/dev/null | grep -E "Total|Used|Free" | tee -a "$LOG_FILE" || true
fi
