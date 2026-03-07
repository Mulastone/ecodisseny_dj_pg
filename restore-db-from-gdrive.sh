#!/usr/bin/env bash
set -Eeuo pipefail

# Restauracion de BBDD desde Google Drive.
# Uso:
#   ./restore-db-from-gdrive.sh
#   ./restore-db-from-gdrive.sh all_databases_20260307_020000.tar.gz
#   AUTO_YES=true ./restore-db-from-gdrive.sh all_databases_20260307_020000.tar.gz

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"

GDRIVE_REMOTE="${GDRIVE_REMOTE:-gdrive:ecodisseny-backups/database}"
RESTORE_DIR="${RESTORE_DIR:-/tmp/restore-db}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
DB_SERVICE="${DB_SERVICE:-db}"
DB_SPECS="${DB_SPECS:-ecodisseny_db:ecodisseny}"
AUTO_YES="${AUTO_YES:-false}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

mkdir -p "$RESTORE_DIR"

if [[ "$COMPOSE_FILE" != /* ]]; then
  COMPOSE_FILE="${PROJECT_DIR}/${COMPOSE_FILE}"
fi
if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="${PROJECT_DIR}/${ENV_FILE}"
fi

if [[ $# -eq 0 ]]; then
  log "Backups disponibles en ${GDRIVE_REMOTE}:"
  rclone ls "$GDRIVE_REMOTE" | grep -E '\.tar\.gz$' | sort -r || true
  echo
  log "Uso: $0 all_databases_YYYYMMDD_HHMMSS.tar.gz"
  exit 0
fi

backup_file="$1"
local_archive="${RESTORE_DIR}/${backup_file}"

log "Descargando backup desde Google Drive..."
rclone copyto "${GDRIVE_REMOTE%/}/${backup_file}" "$local_archive"
log "Descarga completada: $local_archive"

log "Descomprimiendo backup..."
tar -xzf "$local_archive" -C "$RESTORE_DIR"
rm -f "$local_archive"

log "Dumps encontrados:"
find "$RESTORE_DIR" -maxdepth 1 -type f -name "*.sql.gz" -printf " - %f\n" | sort || true

if [[ "$AUTO_YES" != "true" ]]; then
  read -r -p "Esto sobrescribira datos actuales. Continuar? [y/N]: " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    log "Restauracion cancelada."
    rm -rf "$RESTORE_DIR"
    exit 1
  fi
fi

restore_database() {
  local spec="$1"
  local db_name="${spec%%:*}"
  local db_user="${spec##*:}"
  local sql_gz
  sql_gz="$(ls -1 "${RESTORE_DIR}/${db_name}"_*.sql.gz 2>/dev/null | head -n1 || true)"

  if [[ -z "$sql_gz" ]]; then
    log "WARN: no hay dump para ${db_name}. Se omite."
    return 0
  fi

  log "Restaurando ${db_name} con usuario ${db_user}..."
  gunzip -c "$sql_gz" | docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T "$DB_SERVICE" \
    psql -U "$db_user" -d "$db_name"
  log "OK: ${db_name} restaurada."
}

for spec in $DB_SPECS; do
  restore_database "$spec"
done

rm -rf "$RESTORE_DIR"
log "Proceso de restauracion completado."
