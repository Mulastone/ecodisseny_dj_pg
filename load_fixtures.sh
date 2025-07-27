#!/bin/bash

# 📂 Ruta relativa a la carpeta de fixtures de maestros
FIXTURES_DIR="maestros/fixtures"

# 🗂 Lista de archivos a cargar
FIXTURES=(
  tipusrecurso.json
  recurso.json
  parroquia.json
  poblacio.json
  ubicacio.json
  hores.json
  treballs.json
  tasca.json
  tasques_treball.json
  desplacaments.json
  departament_client.json
)

echo "🔄 Carregant fixtures de la app 'maestros'..."

for fixture in "${FIXTURES[@]}"; do
  echo "📥 ${fixture}"
  python manage.py loaddata "${FIXTURES_DIR}/${fixture}"
done

echo "✅ Càrrega de fixtures completada."
