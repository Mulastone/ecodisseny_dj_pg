#!/usr/bin/env bash
set -Eeuo pipefail

# Backup de BBDD a Google Drive usando docker compose (sin nombre de contenedor hardcodeado).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
LOG_FILE="${LOG_FILE:-$LOG_DIR/backup-db-gdrive.log}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/ecodisseny-backups-db}"
DATE="$(date +"%Y%m%d_%H%M%S")"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
DB_SERVICE="${DB_SERVICE:-db}"
DB_SPECS="${DB_SPECS:-ecodisseny_db:ecodisseny}"

GDRIVE_REMOTE="${GDRIVE_REMOTE:-gdrive:ecodisseny-backups/database}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

mkdir -p "$LOG_DIR" "$BACKUP_DIR"
touch "$LOG_FILE"
chmod 640 "$LOG_FILE" 2>/dev/null || true

if [[ "$COMPOSE_FILE" != /* ]]; then
  COMPOSE_FILE="${PROJECT_DIR}/${COMPOSE_FILE}"
fi
if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="${PROJECT_DIR}/${ENV_FILE}"
fi

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

compose_exec() {
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T "$DB_SERVICE" "$@"
}

if ! command -v rclone >/dev/null 2>&1; then
  log "ERROR: rclone no esta instalado."
  exit 1
fi

log "Iniciando backup de base de datos..."

backup_database() {
  local spec="$1"
  local db_name="${spec%%:*}"
  local db_user="${spec##*:}"
  local output_file="${BACKUP_DIR}/${db_name}_${DATE}.sql"

  if [[ -z "$db_name" || -z "$db_user" ]]; then
    log "ERROR: DB_SPECS invalido: $spec (esperado db:user)."
    return 1
  fi

  log "Dump de ${db_name} (usuario ${db_user})..."
  compose_exec pg_dump -U "$db_user" -d "$db_name" >"$output_file"
  gzip -f "$output_file"
  log "OK: ${output_file}.gz"
}

for spec in $DB_SPECS; do
  backup_database "$spec"
done

mapfile -t dump_files < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name "*_${DATE}.sql.gz" -print)
if [[ "${#dump_files[@]}" -eq 0 ]]; then
  log "ERROR: No se generaron dumps SQL."
  exit 1
fi

archive_name="all_databases_${DATE}.tar.gz"
archive_path="${BACKUP_DIR}/${archive_name}"
relative_files=()
for file in "${dump_files[@]}"; do
  relative_files+=("$(basename "$file")")
done
tar -czf "$archive_path" -C "$BACKUP_DIR" "${relative_files[@]}"
rm -f "${dump_files[@]}"
log "Archivo consolidado: ${archive_name}"

log "Subiendo backup a Google Drive (${GDRIVE_REMOTE})..."
rclone copy "$archive_path" "$GDRIVE_REMOTE" \
  --log-level INFO \
  --log-file="$LOG_FILE"
rm -f "$archive_path"
log "OK: backup subido."

log "Aplicando retencion remota (${RETENTION_DAYS} dias)..."
rclone delete "$GDRIVE_REMOTE" \
  --min-age "${RETENTION_DAYS}d" \
  --include "*.tar.gz" \
  --log-file="$LOG_FILE" || log "WARN: no se pudo limpiar historico remoto."

log "Backup de base de datos finalizado."
