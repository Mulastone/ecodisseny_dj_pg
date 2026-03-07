# 🔧 Mantenimiento del Sistema

El mantenimiento regular es esencial para garantizar el rendimiento óptimo y la estabilidad del sistema Ecodisseny.

## 📊 **Monitoreo del Sistema**

### 🖥️ **Estado del Servidor**

#### Recursos del Sistema

```bash
# Verificar uso de memoria
free -h

# Verificar uso de disco
df -h

# Verificar carga del CPU
top

# Verificar procesos de Django
ps aux | grep python
```

#### Métricas Importantes

- **CPU**: < 80% uso promedio
- **Memoria**: < 85% utilización
- **Disco**: < 90% capacidad
- **Base de datos**: Tiempo de respuesta < 200ms

### 📈 **Monitoreo de Aplicación**

#### Logs de Django

```bash
# Ver logs en tiempo real
docker-compose logs -f web

# Buscar errores
docker-compose logs web | grep ERROR

# Análisis de logs por fecha
docker-compose logs --since="2024-01-01" web
```

#### Métricas de Rendimiento

```python
# En Django Admin > Sistema > Métricas
- Tiempo de respuesta promedio
- Número de usuarios activos
- Consultas de base de datos por minuto
- Errores 500 por hora
```

## 💾 **Gestión de Copias de Seguridad**

### 🗄️ **Backup de Base de Datos**

#### Backup Manual

```bash
# Crear backup
docker-compose exec db pg_dump -U postgres ecodisseny > backup_$(date +%Y%m%d).sql

# Comprimir backup
gzip backup_$(date +%Y%m%d).sql
```

#### Backup Automático

```bash
#!/bin/bash
# /usr/local/bin/backup_ecodisseny.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/ecodisseny"
RETENTION_DAYS=30

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup de base de datos
docker-compose exec -T db pg_dump -U postgres ecodisseny | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup de archivos media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Limpiar backups antiguos
find $BACKUP_DIR -type f -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completado: $DATE"
```

#### Configurar Cron

```bash
# Editar crontab
crontab -e

# Agregar backup diario a las 2 AM
0 2 * * * /usr/local/bin/backup_ecodisseny.sh >> /var/log/backup.log 2>&1
```

### 🔄 **Restauración de Backups**

#### Restaurar Base de Datos

```bash
# Detener aplicación
docker-compose down

# Restaurar desde backup
gunzip -c backup_20240815.sql.gz | docker-compose exec -T db psql -U postgres ecodisseny

# Reiniciar aplicación
docker-compose up -d
```

#### Restaurar Archivos

```bash
# Restaurar archivos media
tar -xzf media_20240815.tar.gz -C /
```

## 🧹 **Limpieza y Optimización**

### 🗑️ **Limpieza de Archivos**

#### Logs Antiguos

```bash
# Limpiar logs de Django
find /var/log/ecodisseny/ -name "*.log" -mtime +30 -delete

# Limpiar logs de Docker
docker system prune -a --volumes
```

#### Archivos Temporales

```bash
# Limpiar archivos temporales de Django
docker-compose exec web python manage.py clearsessions

# Limpiar archivos media huérfanos
docker-compose exec web python manage.py cleanup_unused_media
```

### 🏎️ **Optimización de Base de Datos**

#### Mantenimiento Regular

```sql
-- Actualizar estadísticas
ANALYZE;

-- Limpiar espacio no utilizado
VACUUM;

-- Optimización completa (usar con cuidado)
VACUUM FULL;
```

#### Script de Optimización

```python
# management/commands/optimize_db.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE;")
            cursor.execute("VACUUM;")
        self.stdout.write("Base de datos optimizada")
```

## 📦 **Actualizaciones del Sistema**

### 🔄 **Actualización de Dependencias**

#### Python Packages

```bash
# Verificar paquetes desactualizados
docker-compose exec web pip list --outdated

# Actualizar requirements.txt
docker-compose exec web pip freeze > requirements.txt

# Reconstruir contenedor
docker-compose build --no-cache web
```

#### Sistema Operativo

```bash
# Actualizar paquetes del sistema
apt update && apt upgrade -y

# Verificar actualizaciones de seguridad
unattended-upgrades --dry-run
```

### 🚀 **Despliegue de Actualizaciones**

#### Proceso de Actualización

```bash
#!/bin/bash
# Script de despliegue

# 1. Backup antes de actualizar
./backup_ecodisseny.sh

# 2. Detener servicios
docker-compose down

# 3. Actualizar código
git pull origin main

# 4. Reconstruir contenedores
docker-compose build

# 5. Migrar base de datos
docker-compose run web python manage.py migrate

# 6. Recolectar archivos estáticos
docker-compose run web python manage.py collectstatic --noinput

# 7. Reiniciar servicios
docker-compose up -d

echo "Despliegue completado"
```

## 🔍 **Diagnóstico de Problemas**

### 🐛 **Resolución de Errores Comunes**

#### Aplicación No Responde

```bash
# Verificar estado de contenedores
docker-compose ps

# Verificar logs de errores
docker-compose logs web | tail -100

# Reiniciar servicios
docker-compose restart
```

#### Base de Datos Lenta

```sql
-- Verificar consultas lentas
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Verificar bloqueos
SELECT * FROM pg_locks WHERE NOT granted;
```

#### Espacio en Disco Lleno

```bash
# Encontrar archivos grandes
find / -type f -size +100M -exec ls -lh {} \;

# Limpiar logs grandes
truncate -s 0 /var/log/large_log_file.log

# Limpiar Docker
docker system prune -a
```

### 📊 **Herramientas de Diagnóstico**

#### Script de Verificación

```bash
#!/bin/bash
# health_check.sh

echo "=== VERIFICACIÓN DE SALUD DEL SISTEMA ==="

# Verificar contenedores
echo "Contenedores activos:"
docker-compose ps

# Verificar conexión a BD
echo "Conexión a base de datos:"
docker-compose exec db pg_isready -U postgres

# Verificar espacio en disco
echo "Espacio en disco:"
df -h | grep -E "/$|/var"

# Verificar memoria
echo "Uso de memoria:"
free -h

# Verificar aplicación web
echo "Estado de aplicación web:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/

echo "=== VERIFICACIÓN COMPLETADA ==="
```

## 📅 **Tareas de Mantenimiento Programado**

### 🗓️ **Calendario de Mantenimiento**

#### Diario

- [ ] Verificar logs de error
- [ ] Monitorear uso de recursos
- [ ] Backup automático

#### Semanal

- [ ] Revisar métricas de rendimiento
- [ ] Limpiar archivos temporales
- [ ] Verificar integridad de backups

#### Mensual

- [ ] Optimizar base de datos
- [ ] Actualizar dependencias
- [ ] Revisar logs de seguridad
- [ ] Probar restauración de backup

#### Trimestral

- [ ] Actualización mayor del sistema
- [ ] Auditoría de seguridad
- [ ] Revisión de capacidad
- [ ] Documentación de cambios

## 🛠️ **Herramientas de Administración**

### 📊 **Panel de Control**

#### Comandos de Django

```bash
# Estado de migraciones
docker-compose exec web python manage.py showmigrations

# Verificar configuración
docker-compose exec web python manage.py check

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic
```

#### Utilidades Personalizadas

```python
# management/commands/system_status.py
from django.core.management.base import BaseCommand
from django.db import connection
import psutil

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Verificar conexión DB
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Estadísticas del sistema
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()

        self.stdout.write(f"CPU: {cpu_percent}%")
        self.stdout.write(f"Memoria: {memory.percent}%")
```

## 📚 **Documentación de Procedimientos**

### 📝 **Registro de Cambios**

#### Template de Cambio

```markdown
## Cambio: [Título]

**Fecha**: YYYY-MM-DD
**Responsable**: [Nombre]
**Tipo**: [Mantenimiento/Actualización/Corrección]

### Descripción

[Descripción detallada del cambio]

### Impacto

[Impacto en usuarios y sistema]

### Rollback

[Procedimiento de reversión si es necesario]

### Verificación

[Pasos para verificar que el cambio fue exitoso]
```

## 🆘 **Contactos de Emergencia**

### 📞 **Escalación de Incidentes**

#### Nivel 1 - Administrador del Sistema

- **Contacto**: admin@ecodisseny.com
- **Horario**: 8:00 - 18:00

#### Nivel 2 - Soporte Técnico

- **Contacto**: soporte@ecodisseny.com
- **Horario**: 24/7

#### Nivel 3 - Desarrollador Principal

- **Contacto**: dev@ecodisseny.com
- **Horario**: Emergencias únicamente

## 📚 **Recursos Adicionales**

- [Configuración del Sistema](/documentacion/admin/configuracion-del-sistema/)
- [Seguridad](/documentacion/admin/seguridad/)
- [Gestión de Usuarios](/documentacion/admin/gestion-de-usuarios/)

---

_🔧 **Importante**: Mantén esta documentación actualizada con cualquier cambio en los procedimientos._
