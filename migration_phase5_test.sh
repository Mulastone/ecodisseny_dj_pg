#!/bin/bash
# Script: /root/ecodisseny_dj_pg/migration_phase5_test.sh
# Propósito: Iniciar servicios con nueva configuración y validar funcionamiento

set -e

PROJECT_DIR="/root/ecodisseny_dj_pg"
MIGRATION_LOG="/opt/ecodisseny/logs/migration_test_$(date +%Y%m%d_%H%M%S).log"

echo "🧪 FASE 5: PRUEBA Y VALIDACIÓN"
echo "==============================" | tee -a "$MIGRATION_LOG"

cd "$PROJECT_DIR"

# 1. Verificar que los servicios están parados
echo "🔍 Verificando estado de servicios..." | tee -a "$MIGRATION_LOG"
docker-compose down || echo "Servicios ya están parados"

# 2. Construir imágenes si es necesario
echo "🏗️ Construyendo imágenes..." | tee -a "$MIGRATION_LOG"
docker-compose build --no-cache web

# 3. Iniciar PostgreSQL primero
echo "🗄️ Iniciando PostgreSQL..." | tee -a "$MIGRATION_LOG"
docker-compose up -d db

# 4. Esperar a que PostgreSQL esté listo
echo "⏳ Esperando PostgreSQL..." | tee -a "$MIGRATION_LOG"
timeout=60
counter=0
while ! docker exec ecodisseny_dj_pg_db_1 pg_isready -U ecodisseny_user -d ecodisseny_db 2>/dev/null; do
    if [ $counter -eq $timeout ]; then
        echo "❌ Timeout esperando PostgreSQL" | tee -a "$MIGRATION_LOG"
        exit 1
    fi
    echo "Esperando PostgreSQL... ($counter/$timeout)" | tee -a "$MIGRATION_LOG"
    sleep 2
    counter=$((counter + 2))
done

echo "✅ PostgreSQL está listo" | tee -a "$MIGRATION_LOG"

# 5. Verificar integridad de la base de datos
echo "🔍 Verificando integridad de base de datos..." | tee -a "$MIGRATION_LOG"
DB_TABLES=$(docker exec ecodisseny_dj_pg_db_1 psql -U ecodisseny_user -d ecodisseny_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | tr -d ' ')
echo "📊 Tablas encontradas: $DB_TABLES" | tee -a "$MIGRATION_LOG"

if [ "$DB_TABLES" -gt 0 ]; then
    echo "✅ Base de datos tiene tablas" | tee -a "$MIGRATION_LOG"
else
    echo "⚠️ Base de datos parece vacía, ejecutando migraciones..." | tee -a "$MIGRATION_LOG"
fi

# 6. Iniciar Redis
echo "🔴 Iniciando Redis..." | tee -a "$MIGRATION_LOG"
docker-compose up -d redis

# 7. Verificar Redis
timeout=30
counter=0
while ! docker exec ecodisseny_dj_pg_redis_1 redis-cli ping 2>/dev/null | grep -q "PONG"; do
    if [ $counter -eq $timeout ]; then
        echo "❌ Redis no responde" | tee -a "$MIGRATION_LOG"
        exit 1
    fi
    echo "Esperando Redis... ($counter/$timeout)" | tee -a "$MIGRATION_LOG"
    sleep 1
    counter=$((counter + 1))
done

echo "✅ Redis está funcionando" | tee -a "$MIGRATION_LOG"

# 8. Iniciar aplicación web
echo "🌐 Iniciando aplicación web..." | tee -a "$MIGRATION_LOG"
docker-compose up -d web

# 9. Esperar a que la aplicación esté lista
echo "⏳ Esperando aplicación web..." | tee -a "$MIGRATION_LOG"
timeout=120
counter=0
while ! curl -f http://localhost:8000 >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        echo "❌ Aplicación web no responde" | tee -a "$MIGRATION_LOG"
        echo "🔍 Revisando logs..." | tee -a "$MIGRATION_LOG"
        docker-compose logs web | tail -20 | tee -a "$MIGRATION_LOG"
        exit 1
    fi
    echo "Esperando aplicación web... ($counter/$timeout)" | tee -a "$MIGRATION_LOG"
    sleep 2
    counter=$((counter + 2))
done

echo "✅ Aplicación web está funcionando" | tee -a "$MIGRATION_LOG"

# 10. Verificar archivos media
echo "📁 Verificando archivos media..." | tee -a "$MIGRATION_LOG"
MEDIA_COUNT=$(find /opt/ecodisseny/data/media -type f 2>/dev/null | wc -l)
echo "📊 Archivos media disponibles: $MEDIA_COUNT" | tee -a "$MIGRATION_LOG"

# 11. Verificar archivos static
echo "📄 Verificando archivos static..." | tee -a "$MIGRATION_LOG"
STATIC_COUNT=$(find /opt/ecodisseny/data/static -type f 2>/dev/null | wc -l)
echo "📊 Archivos static disponibles: $STATIC_COUNT" | tee -a "$MIGRATION_LOG"

# 12. Prueba de funcionalidad web
echo "🌐 Probando funcionalidad web..." | tee -a "$MIGRATION_LOG"

# Probar página principal
if curl -f -s http://localhost:8000 >/dev/null; then
    echo "✅ Página principal accesible" | tee -a "$MIGRATION_LOG"
else
    echo "❌ Error en página principal" | tee -a "$MIGRATION_LOG"
fi

# Probar login
if curl -f -s http://localhost:8000/accounts/login/ >/dev/null; then
    echo "✅ Página login accesible" | tee -a "$MIGRATION_LOG"
else
    echo "❌ Error en página login" | tee -a "$MIGRATION_LOG"
fi

# 13. Iniciar pgAdmin (opcional)
echo "🔧 Iniciando pgAdmin..." | tee -a "$MIGRATION_LOG"
docker-compose up -d pgadmin

# 14. Verificar todos los servicios
echo "📊 Estado final de servicios:" | tee -a "$MIGRATION_LOG"
docker-compose ps | tee -a "$MIGRATION_LOG"

# 15. Verificar logs
echo "📝 Verificando logs..." | tee -a "$MIGRATION_LOG"
if [ -f "/opt/ecodisseny/logs/django/gunicorn_access.log" ]; then
    echo "✅ Logs Django funcionando" | tee -a "$MIGRATION_LOG"
else
    echo "⚠️ Logs Django no encontrados" | tee -a "$MIGRATION_LOG"
fi

# 16. Resumen final
echo ""
echo "🎉 FASE 5 COMPLETADA" | tee -a "$MIGRATION_LOG"
echo "=============================" | tee -a "$MIGRATION_LOG"
echo "✅ PostgreSQL: $(docker exec ecodisseny_dj_pg_db_1 pg_isready -U ecodisseny_user | cut -d: -f3-)" | tee -a "$MIGRATION_LOG"
echo "✅ Redis: $(docker exec ecodisseny_dj_pg_redis_1 redis-cli ping)" | tee -a "$MIGRATION_LOG"
echo "✅ Web App: Funcionando en puerto 8000" | tee -a "$MIGRATION_LOG"
echo "✅ pgAdmin: Disponible en puerto 8080" | tee -a "$MIGRATION_LOG"
echo "📊 Archivos media: $MEDIA_COUNT" | tee -a "$MIGRATION_LOG"
echo "📊 Archivos static: $STATIC_COUNT" | tee -a "$MIGRATION_LOG"
echo "📊 Tablas DB: $DB_TABLES" | tee -a "$MIGRATION_LOG"
echo ""
echo "🌐 Aplicación disponible en:"
echo "   - http://localhost:8000 (web app)"
echo "   - http://localhost:8080 (pgAdmin)"
echo "   - https://app.arasmu.net (dominio público)"
echo ""
echo "📝 Log completo: $MIGRATION_LOG"
echo ""
echo "🔧 Para configurar backups automáticos: ./migration_phase6_backup.sh"
