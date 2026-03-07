#!/usr/bin/env bash
set -Eeuo pipefail

# Reset al estado base (sin restaurar backups):
# - elimina solo el volumen de DB del proyecto
# - vuelve a levantar stack
# - aplica migrate
# - carga fixtures base (opcional)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
DB_LOGICAL_VOLUME="${DB_LOGICAL_VOLUME:-postgres_data}"
LOAD_FIXTURES="${LOAD_FIXTURES:-true}"

if [[ "$COMPOSE_FILE" != /* ]]; then
  COMPOSE_FILE="${PROJECT_DIR}/${COMPOSE_FILE}"
fi
if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="${PROJECT_DIR}/${ENV_FILE}"
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "ERROR: No existe COMPOSE_FILE: $COMPOSE_FILE"
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: No existe ENV_FILE: $ENV_FILE"
  exit 1
fi

cd "$PROJECT_DIR"

compose() {
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
}

project_name="${COMPOSE_PROJECT_NAME:-$(basename "$PROJECT_DIR")}" 

echo "ATENCION: este proceso reinicia la base de datos del proyecto '${project_name}'."
echo "Se conservaran los archivos del codigo; se pierde contenido de DB actual."
read -r -p "Escribe RESET-BASE para continuar: " confirm
if [[ "$confirm" != "RESET-BASE" ]]; then
  echo "Cancelado."
  exit 1
fi

echo "[1/5] Deteniendo stack..."
compose down

echo "[2/5] Buscando volumen de DB (${DB_LOGICAL_VOLUME})..."
mapfile -t db_volumes < <(docker volume ls -q \
  --filter "label=com.docker.compose.project=${project_name}" \
  --filter "label=com.docker.compose.volume=${DB_LOGICAL_VOLUME}")

if [[ "${#db_volumes[@]}" -eq 0 ]]; then
  candidate="${project_name}_${DB_LOGICAL_VOLUME}"
  if docker volume inspect "$candidate" >/dev/null 2>&1; then
    db_volumes=("$candidate")
  fi
fi

if [[ "${#db_volumes[@]}" -eq 0 ]]; then
  echo "ERROR: no se encontro volumen DB para proyecto=${project_name}, volumen=${DB_LOGICAL_VOLUME}."
  echo "Tip: exporta COMPOSE_PROJECT_NAME o DB_LOGICAL_VOLUME si tu stack usa otro nombre."
  exit 1
fi

echo "Volumen(es) DB a eliminar: ${db_volumes[*]}"
for v in "${db_volumes[@]}"; do
  docker volume rm "$v"
done

echo "[3/5] Levantando stack limpio..."
compose up -d --build

echo "[4/5] Aplicando migraciones..."
compose exec -T web python manage.py migrate

if [[ "$LOAD_FIXTURES" == "true" ]]; then
  echo "[5/5] Cargando fixtures base..."
  compose exec -T web ./docker-load-fixtures.sh
else
  echo "[5/5] Saltando fixtures (LOAD_FIXTURES=$LOAD_FIXTURES)."
fi

echo "Reset base completado."
