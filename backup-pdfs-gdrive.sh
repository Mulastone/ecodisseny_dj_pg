#!/usr/bin/env bash
set -Eeuo pipefail

# Backup de PDFs a Google Drive.
# Usa copy (no sync) para evitar borrados accidentales en remoto.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
LOG_FILE="${LOG_FILE:-$LOG_DIR/backup-pdfs-gdrive.log}"

SOURCE_DIR="${SOURCE_DIR:-$PROJECT_DIR/media/pdfs_pressupostos}"
GDRIVE_REMOTE_ROOT="${GDRIVE_REMOTE_ROOT:-gdrive:ecodisseny-backups/pdfs}"
REMOTE_LATEST_DIR="${REMOTE_LATEST_DIR:-latest}"
DEST_REMOTE="${GDRIVE_REMOTE_ROOT%/}/${REMOTE_LATEST_DIR}"

PDFS_CREATE_SNAPSHOT="${PDFS_CREATE_SNAPSHOT:-false}"
SNAPSHOT_RETENTION_DAYS="${SNAPSHOT_RETENTION_DAYS:-30}"
DATE_TAG="$(date '+%Y%m%d_%H%M%S')"

mkdir -p "$LOG_DIR"
touch "$LOG_FILE"
chmod 640 "$LOG_FILE" 2>/dev/null || true

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

if ! command -v rclone >/dev/null 2>&1; then
  log "ERROR: rclone no esta instalado."
  exit 1
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  log "ERROR: Directorio fuente no existe: $SOURCE_DIR"
  exit 1
fi

log "Iniciando backup de PDFs: $SOURCE_DIR -> $DEST_REMOTE"
rclone copy "$SOURCE_DIR" "$DEST_REMOTE" \
  --log-level INFO \
  --log-file="$LOG_FILE" \
  --transfers 4 \
  --checkers 8 \
  --checksum \
  --update \
  --create-empty-src-dirs
log "OK: backup de PDFs (latest) completado."

if [[ "$PDFS_CREATE_SNAPSHOT" == "true" ]]; then
  snapshot_remote="${GDRIVE_REMOTE_ROOT%/}/snapshots/${DATE_TAG}"
  log "Creando snapshot adicional en ${snapshot_remote}"
  rclone copy "$SOURCE_DIR" "$snapshot_remote" \
    --log-level INFO \
    --log-file="$LOG_FILE" \
    --transfers 4 \
    --checkers 8 \
    --checksum \
    --create-empty-src-dirs

  log "Aplicando retencion de snapshots (${SNAPSHOT_RETENTION_DAYS} dias)"
  rclone delete "${GDRIVE_REMOTE_ROOT%/}/snapshots" \
    --min-age "${SNAPSHOT_RETENTION_DAYS}d" \
    --log-file="$LOG_FILE" || log "WARN: no se pudo limpiar snapshots antiguos."
fi

total_size="$(du -sh "$SOURCE_DIR" | awk '{print $1}')"
log "Tamano respaldado: ${total_size}"
