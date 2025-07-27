#!/bin/bash

# ---------------------------------------------
# Reinicio completo del proyecto Django Ecodisseny
# ---------------------------------------------

echo "🚨 Este script borrará TODAS las migraciones de tus apps y reiniciará la base de datos."
read -p "¿Estás seguro? (s/n): " confirm
if [[ $confirm != "s" ]]; then
  echo "❌ Cancelado."
  exit 1
fi

# Verifica que esté en la raíz del proyecto
if [[ ! -f "manage.py" ]]; then
  echo "❌ No se encontró manage.py. ¿Estás en la raíz del proyecto?"
  exit 1
fi

# Verifica entorno virtual
if [[ ! -d "venv_postgres" ]]; then
  echo "❌ No se encontró el entorno virtual en ./venv_postgres"
  exit 1
fi

echo "🧹 Borrando archivos de migraciones..."
find ./maestros -path "*/migrations/*.py" -not -name "__init__.py" -delete
find ./maestros -path "*/migrations/*.pyc" -delete

find ./pressupostos -path "*/migrations/*.py" -not -name "__init__.py" -delete
find ./pressupostos -path "*/migrations/*.pyc" -delete

find ./projectes -path "*/migrations/*.py" -not -name "__init__.py" -delete
find ./projectes -path "*/migrations/*.pyc" -delete

echo "🧹 Borrando __pycache__..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null

read -p "¿Querés borrar y crear una base de datos nueva en PostgreSQL? (s/n): " dbconfirm
if [[ $dbconfirm == "s" ]]; then
  read -p "Nombre de la base de datos: " dbname
  read -p "Usuario propietario (ej. ecodisseny): " dbuser
  read -s -p "Contraseña del usuario PostgreSQL: " dbpass
  echo
  export PGPASSWORD="$dbpass"

  echo "🗃️ Haciendo backup en ${dbname}_backup.sql..."
  pg_dump -U "$dbuser" "$dbname" > "${dbname}_backup.sql" 2>>reset_errors.log

  echo "🗑️ Borrando base de datos '$dbname' (si existe)..."
  sudo -u postgres psql -c "DROP DATABASE IF EXISTS $dbname;" 2>>reset_errors.log

  echo "🆕 Creando base de datos '$dbname'..."
  sudo -u postgres createdb -O "$dbuser" "$dbname" 2>>reset_errors.log
fi

echo "⚙️ Activando entorno virtual..."
source ./venv_postgres/bin/activate

echo "⚙️ Ejecutando makemigrations y migrate..."
python manage.py makemigrations 2>>reset_errors.log
python manage.py migrate 2>>reset_errors.log

echo "✅ Migraciones reiniciadas y base de datos limpia."

if [[ -s reset_errors.log ]]; then
  echo "⚠️ Se encontraron errores. Consultá reset_errors.log para más detalles."
fi
