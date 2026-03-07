#!/usr/bin/env bash
set -Eeuo pipefail

# Restauracion de PDFs desde Google Drive.
# Uso:
#   ./restore-pdfs-from-gdrive.sh
#   ./restore-pdfs-from-gdrive.sh gdrive:ecodisseny-backups/pdfs/latest
#   AUTO_YES=true ./restore-pdfs-from-gdrive.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"

SOURCE_REMOTE="${1:-${SOURCE_REMOTE:-gdrive:ecodisseny-backups/pdfs/latest}}"
DEST_DIR="${DEST_DIR:-$PROJECT_DIR/media/pdfs_pressupostos}"
AUTO_YES="${AUTO_YES:-false}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

if ! command -v rclone >/dev/null 2>&1; then
  log "ERROR: rclone no esta instalado."
  exit 1
fi

mkdir -p "$DEST_DIR"

if [[ "$AUTO_YES" != "true" ]]; then
  read -r -p "Se copiaran PDFs de ${SOURCE_REMOTE} a ${DEST_DIR}. Continuar? [y/N]: " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    log "Restauracion cancelada."
    exit 1
  fi
fi

log "Iniciando restauracion de PDFs..."
rclone copy "$SOURCE_REMOTE" "$DEST_DIR" \
  --transfers 4 \
  --checkers 8 \
  --checksum \
  --create-empty-src-dirs

count_files="$(find "$DEST_DIR" -type f | wc -l | awk '{print $1}')"
log "Restauracion finalizada. Archivos en destino: ${count_files}"
