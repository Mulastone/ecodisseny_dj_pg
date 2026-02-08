#!/bin/bash

# Script para restaurar base de datos desde Google Drive
# USO: ./restore-db-from-gdrive.sh [fecha]
# Ejemplo: ./restore-db-from-gdrive.sh 20260208
# Si no se especifica fecha, muestra los backups disponibles

GDRIVE_REMOTE="gdrive:ecodisseny-backups/database"
RESTORE_DIR="/tmp/restore-db"
CONTAINER_NAME="ecodisseny_dj_pg_db_1"

# Crear directorio temporal
mkdir -p $RESTORE_DIR

# Si no se especifica archivo, listar backups disponibles
if [ -z "$1" ]; then
    echo "📦 Backups disponibles en Google Drive:"
    echo "========================================"
    rclone ls "$GDRIVE_REMOTE" | grep ".tar.gz" | sort -r
    echo ""
    echo "💡 Uso: $0 [fecha_archivo]"
    echo "   Ejemplo: $0 all_databases_20260208_140000.tar.gz"
    exit 0
fi

BACKUP_FILE="$1"

echo "🔄 Descargando backup desde Google Drive..."
rclone copy "${GDRIVE_REMOTE}/${BACKUP_FILE}" "$RESTORE_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Error al descargar el backup"
    exit 1
fi

echo "✓ Backup descargado"

# Descomprimir
cd $RESTORE_DIR
echo "📦 Descomprimiendo archivo..."
tar -xzf "$BACKUP_FILE"

if [ $? -ne 0 ]; then
    echo "❌ Error al descomprimir el backup"
    exit 1
fi

echo "✓ Archivo descomprimido"

# Función para restaurar una base de datos
restore_database() {
    local db_name=$1
    local db_user=$2
    local sql_file=$(ls ${RESTORE_DIR}/${db_name}_*.sql.gz 2>/dev/null | head -n1)
    
    if [ -z "$sql_file" ]; then
        echo "⚠️  No se encontró backup para $db_name"
        return 1
    fi
    
    echo "🔄 Restaurando $db_name desde $sql_file..."
    
    # Descomprimir SQL
    gunzip "$sql_file"
    sql_file="${sql_file%.gz}"
    
    # Confirmar antes de restaurar
    read -p "⚠️  ¿SEGURO que quieres restaurar $db_name? Esto SOBREESCRIBIRÁ los datos actuales [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Restauración cancelada"
        return 1
    fi
    
    # Restaurar
    docker exec -i $CONTAINER_NAME psql -U $db_user -d $db_name < "$sql_file"
    
    if [ $? -eq 0 ]; then
        echo "✅ $db_name restaurada exitosamente"
    else
        echo "❌ Error al restaurar $db_name"
        return 1
    fi
}

# Restaurar bases de datos
echo ""
echo "📊 Bases de datos encontradas en el backup:"
ls $RESTORE_DIR/*.sql 2>/dev/null || ls $RESTORE_DIR/*.sql.gz 2>/dev/null
echo ""

# Preguntar qué restaurar
read -p "¿Restaurar ecodisseny_db? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    restore_database "ecodisseny_db" "ecodisseny_user"
fi

read -p "¿Restaurar properties_db? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    restore_database "properties_db" "scraper_user"
fi

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
rm -rf $RESTORE_DIR

echo "✅ Proceso de restauración completado"
