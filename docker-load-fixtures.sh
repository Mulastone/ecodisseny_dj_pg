#!/bin/bash

# Script para cargar fixtures en entorno Docker
echo "🐳 Cargando fixtures en Docker..."

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
  if [ $? -ne 0 ]; then
    echo "❌ Error cargando ${fixture}"
    exit 1
  fi
done

echo "✅ Càrrega de fixtures completada."

echo ""
echo "🔑 Creando usuarios y perfiles..."
python create_users_profiles.py

if [ $? -eq 0 ]; then
  echo ""
  echo "🎉 ¡Inicialización Docker completa!"
  echo "   • Fixtures cargados"
  echo "   • Usuarios creados"  
  echo "   • Perfiles configurados"
  echo "   • Contraseña para todos: ecodisseny2024"
  echo "   • Accede a: http://localhost:8000"
else
  echo "❌ Error creando usuarios y perfiles"
  exit 1
fi
