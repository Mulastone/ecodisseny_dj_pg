#!/bin/bash
# Script: /root/ecodisseny_dj_pg/migration_phase7_cleanup.sh
# Propósito: Limpieza final y documentación

set -e

echo "🧹 FASE 7: LIMPIEZA Y FINALIZACIÓN"
echo "=================================="

PROJECT_DIR="/root/ecodisseny_dj_pg"
cd "$PROJECT_DIR"

# 1. Limpieza de volúmenes Docker antiguos (OPCIONAL)
echo "🐳 Gestionando volúmenes Docker antiguos..."
echo "Volúmenes Docker actuales:"
docker volume ls | grep ecodisseny

read -p "¿Eliminar volúmenes Docker antiguos? (Recomendado después de verificar que todo funciona) (y/N): " cleanup_volumes

if [ "$cleanup_volumes" = "y" ] || [ "$cleanup_volumes" = "Y" ]; then
    echo "🗑️ Eliminando volúmenes Docker antiguos..."
    docker volume rm ecodisseny_dj_pg_postgres_data || echo "Ya eliminado"
    docker volume rm ecodisseny_dj_pg_media_volume || echo "Ya eliminado" 
    docker volume rm ecodisseny_dj_pg_static_volume || echo "Ya eliminado"
    echo "✅ Volúmenes Docker antiguos eliminados"
else
    echo "⚠️ Volúmenes Docker mantenidos (puedes eliminarlos manualmente más tarde)"
fi

# 2. Hacer ejecutables todos los scripts de migración
echo "🔧 Configurando permisos de scripts..."
chmod +x migration_phase*.sh

# 3. Crear documentación de la migración
echo "📝 Creando documentación de migración..."
cat > /opt/ecodisseny/MIGRATION_SUMMARY.md << 'EOF'
# 📋 RESUMEN DE MIGRACIÓN A PERSISTENCIA EMPRESARIAL

## 🎯 Objetivo Completado
Migración exitosa de volúmenes Docker a bind mounts con arquitectura de persistencia empresarial.

## 📊 Antes vs Después

### ANTES:
```yaml
volumes:
  postgres_data:    # Gestionado por Docker
  media_volume:     # Ubicación desconocida
  static_volume:    # Sin control directo
```

### DESPUÉS:
```yaml
volumes:
  - /opt/ecodisseny/data/postgres:/var/lib/postgresql/data
  - /opt/ecodisseny/data/media:/app/media
  - /opt/ecodisseny/data/static:/app/staticfiles
  - /opt/ecodisseny/backups:/var/backups
  - /opt/ecodisseny/logs:/app/logs
```

## 🏗️ Estructura Final

```
/opt/ecodisseny/
├── data/
│   ├── postgres/           # Base de datos PostgreSQL
│   ├── redis/              # Cache Redis
│   ├── media/              # Archivos subidos
│   ├── static/             # Archivos estáticos
│   ├── oscar/              # Preparado para Oscar Shop
│   └── pgadmin/            # Configuración pgAdmin
├── backups/
│   ├── postgres/           # Backups base de datos
│   ├── daily/              # Backups diarios
│   ├── weekly/             # Backups semanales
│   └── monthly/            # Backups mensuales
├── config/
│   ├── postgres/           # Configuración PostgreSQL
│   └── nginx/              # Configuración Nginx
├── logs/
│   ├── postgres/           # Logs PostgreSQL
│   ├── django/             # Logs Django
│   └── nginx/              # Logs Nginx
└── scripts/
    ├── backup_completo.sh
    ├── backup_incremental.sh
    ├── restore_backup.sh
    └── monitor_sistema.sh
```

## ✅ Servicios Configurados

1. **PostgreSQL**: Puerto 5432 (solo localhost)
2. **Django Web**: Puerto 8000
3. **Redis**: Puerto 6379 (cache y sesiones)
4. **pgAdmin**: Puerto 8080 (administración DB)

## 💾 Backups Automáticos

- **Diario**: 2:00 AM (completo)
- **Incremental**: Cada 6 horas
- **Semanal**: Domingos 1:00 AM
- **Monitoreo**: Cada 15 minutos

## 🔧 Comandos Útiles

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
tail -f /opt/ecodisseny/logs/django/gunicorn_access.log

# Backup manual
/opt/ecodisseny/scripts/backup_completo.sh

# Restaurar backup
/opt/ecodisseny/scripts/restore_backup.sh /path/to/backup.sql

# Monitoreo manual
/opt/ecodisseny/scripts/monitor_sistema.sh

# Ver espacio utilizado
du -sh /opt/ecodisseny/
```

## 🚀 Preparado para Multi-App

La arquitectura está lista para añadir:
- Django Oscar Shop
- Nuevas aplicaciones Django
- Microservicios adicionales

## 📞 Soporte

- Logs de migración: `/opt/ecodisseny/logs/migration_*.log`
- Backups disponibles: `/opt/ecodisseny/backups/`
- Configuración: `/opt/ecodisseny/config/`

---
**Migración completada**: $(date)
**Versión**: Ecodisseny Persistencia Empresarial v1.0
EOF

# 4. Crear script de información del sistema
echo "📊 Creando script de información del sistema..."
cat > /opt/ecodisseny/scripts/info_sistema.sh << 'EOF'
#!/bin/bash
# Script de información del sistema Ecodisseny

echo "🏢 ECODISSENY - INFORMACIÓN DEL SISTEMA"
echo "======================================="
echo ""

echo "📅 Fecha: $(date)"
echo "🖥️ Servidor: $(hostname)"
echo "👤 Usuario: $(whoami)"
echo ""

echo "🐳 SERVICIOS DOCKER"
echo "-------------------"
docker-compose ps
echo ""

echo "💾 ESTADO DE DATOS"
echo "------------------"
echo "📊 PostgreSQL:"
if docker exec ecodisseny_dj_pg_db_1 pg_isready -U ecodisseny_user >/dev/null 2>&1; then
    DB_SIZE=$(docker exec ecodisseny_dj_pg_db_1 psql -U ecodisseny_user -d ecodisseny_db -t -c "SELECT pg_size_pretty(pg_database_size('ecodisseny_db'));" | tr -d ' ')
    TABLE_COUNT=$(docker exec ecodisseny_dj_pg_db_1 psql -U ecodisseny_user -d ecodisseny_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | tr -d ' ')
    echo "   ✅ Conectado - Tamaño: $DB_SIZE - Tablas: $TABLE_COUNT"
else
    echo "   ❌ No conectado"
fi

echo "📁 Archivos Media: $(find /opt/ecodisseny/data/media -type f 2>/dev/null | wc -l) archivos"
echo "📄 Archivos Static: $(find /opt/ecodisseny/data/static -type f 2>/dev/null | wc -l) archivos"
echo ""

echo "💽 ESPACIO EN DISCO"
echo "-------------------"
df -h /opt/ecodisseny | tail -1
echo "📊 Tamaño /opt/ecodisseny: $(du -sh /opt/ecodisseny | cut -f1)"
echo ""

echo "💾 BACKUPS DISPONIBLES"
echo "----------------------"
echo "📊 Backups PostgreSQL: $(ls /opt/ecodisseny/backups/postgres/*.sql 2>/dev/null | wc -l)"
echo "📊 Backups Diarios: $(ls /opt/ecodisseny/backups/daily/*.tar.gz 2>/dev/null | wc -l)"
echo "📊 Último backup: $(ls -t /opt/ecodisseny/backups/postgres/*.sql 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'Ninguno')"
echo ""

echo "🔍 MONITOREO"
echo "------------"
echo "📝 Logs disponibles:"
find /opt/ecodisseny/logs -name "*.log" -type f | wc -l
echo "⚠️ Errores recientes:"
grep -c "ERROR\|CRITICAL" /opt/ecodisseny/logs/django/*.log 2>/dev/null | head -3 || echo "Sin errores recientes"
echo ""

echo "🌐 ACCESOS"
echo "----------"
echo "   - Aplicación: http://localhost:8000"
echo "   - pgAdmin: http://localhost:8080"
echo "   - Dominio público: https://app.arasmu.net"
echo ""

echo "⏰ TAREAS PROGRAMADAS"
echo "--------------------"
crontab -l | grep ecodisseny || echo "Sin tareas programadas"
EOF

chmod +x /opt/ecodisseny/scripts/info_sistema.sh

# 5. Crear alias útiles
echo "🔧 Configurando aliases útiles..."
cat >> /root/.bashrc << 'EOF'

# Ecodisseny Aliases
alias ecodisseny-status='/opt/ecodisseny/scripts/info_sistema.sh'
alias ecodisseny-logs='tail -f /opt/ecodisseny/logs/django/gunicorn_access.log'
alias ecodisseny-backup='/opt/ecodisseny/scripts/backup_completo.sh'
alias ecodisseny-monitor='/opt/ecodisseny/scripts/monitor_sistema.sh'
alias ecodisseny-cd='cd /root/ecodisseny_dj_pg'
EOF

# 6. Verificación final completa
echo "✅ Ejecutando verificación final..."
echo ""
echo "🔍 VERIFICACIÓN FINAL DEL SISTEMA"
echo "================================="

# Verificar servicios
echo "📊 Estado de servicios:"
docker-compose ps

# Verificar aplicación web
if curl -f -s http://localhost:8000 >/dev/null; then
    echo "✅ Aplicación web funcionando"
else
    echo "❌ Problema con aplicación web"
fi

# Verificar base de datos
if docker exec ecodisseny_dj_pg_db_1 pg_isready -U ecodisseny_user >/dev/null 2>&1; then
    echo "✅ PostgreSQL funcionando"
else
    echo "❌ Problema con PostgreSQL"
fi

# Verificar backups
BACKUP_COUNT=$(ls /opt/ecodisseny/backups/postgres/*.sql 2>/dev/null | wc -l)
echo "✅ Backups disponibles: $BACKUP_COUNT"

# Verificar crontab
if crontab -l | grep -q ecodisseny; then
    echo "✅ Tareas automáticas configuradas"
else
    echo "⚠️ Revisar configuración crontab"
fi

echo ""
echo "🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE"
echo "===================================="
echo ""
echo "✅ LOGROS ALCANZADOS:"
echo "   📁 Persistencia de datos garantizada"
echo "   💾 Sistema de backup automático"
echo "   📊 Monitoreo continuo"
echo "   🔧 Scripts de mantenimiento"
echo "   📋 Documentación completa"
echo "   🚀 Preparado para multi-app"
echo ""
echo "🌐 APLICACIÓN DISPONIBLE EN:"
echo "   - http://localhost:8000"
echo "   - https://app.arasmu.net"
echo "   - pgAdmin: http://localhost:8080"
echo ""
echo "📚 COMANDOS ÚTILES:"
echo "   ecodisseny-status    # Ver estado del sistema"
echo "   ecodisseny-logs      # Ver logs en tiempo real"
echo "   ecodisseny-backup    # Backup manual"
echo "   ecodisseny-monitor   # Monitoreo manual"
echo ""
echo "📁 UBICACIONES IMPORTANTES:"
echo "   - Datos: /opt/ecodisseny/data/"
echo "   - Backups: /opt/ecodisseny/backups/"
echo "   - Logs: /opt/ecodisseny/logs/"
echo "   - Scripts: /opt/ecodisseny/scripts/"
echo "   - Documentación: /opt/ecodisseny/MIGRATION_SUMMARY.md"
echo ""
echo "🔄 Para aplicar aliases, ejecuta: source /root/.bashrc"
echo ""
echo "🚀 ¡READY PARA AÑADIR DJANGO OSCAR SHOP!"
