#!/bin/bash

# Script para backup de todas las bases de datos
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/root/backups"

mkdir -p $BACKUP_DIR

echo "🔄 Iniciando backup de todas las bases de datos..."

# Backup ecodisseny_db
echo "📦 Backup ecodisseny_db..."
docker exec ecodisseny_dj_pg_db_1 pg_dump -U ecodisseny_user -d ecodisseny_db > $BACKUP_DIR/ecodisseny_db_$DATE.sql

# Backup properties_db  
echo "📦 Backup properties_db..."
docker exec ecodisseny_dj_pg_db_1 pg_dump -U scraper_user -d properties_db > $BACKUP_DIR/properties_db_$DATE.sql

# Comprimir backups
echo "🗜️ Comprimiendo backups..."
cd $BACKUP_DIR
tar -czf all_databases_$DATE.tar.gz *_$DATE.sql
rm *_$DATE.sql

echo "✅ Backup completado: all_databases_$DATE.tar.gz"
echo "📍 Ubicación: $BACKUP_DIR/all_databases_$DATE.tar.gz"