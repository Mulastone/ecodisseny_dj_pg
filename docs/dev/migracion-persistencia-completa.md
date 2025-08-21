# 🚀 Migración a Persistencia Empresarial - Ecodisseny

## 📋 Resumen Ejecutivo

Este documento describe la **migración completa** de la aplicación Ecodisseny desde volúmenes Docker gestionados internamente hacia una **arquitectura de persistencia empresarial** con bind mounts explícitos, sistema de backup automático y preparación para multi-aplicación.

### 🎯 Objetivos de la Migración

- **✅ Persistencia garantizada**: Datos en ubicaciones conocidas y controladas
- **✅ Backup automático**: Sistema robusto de respaldo y recuperación
- **✅ Escalabilidad**: Preparación para Django Oscar Shop
- **✅ Monitoreo**: Supervisión continua del sistema
- **✅ Mantenimiento**: Scripts automatizados de administración

---

## 📊 Situación Antes vs Después

### 🔴 ANTES: Volúmenes Docker Internos

```yaml
# docker-compose.yml
services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data # ❌ Ubicación desconocida
  web:
    volumes:
      - static_volume:/app/staticfiles # ❌ Sin control directo
      - media_volume:/app/media # ❌ Backup complicado

volumes:
  postgres_data: # ❌ /var/lib/docker/volumes/[hash]/_data
  static_volume: # ❌ Gestionado internamente por Docker
  media_volume: # ❌ Acceso difícil para backup
```

**Problemas identificados:**

- 📍 Ubicación de datos incierta
- 💾 Backup manual y complicado
- 🔧 Migración entre servidores difícil
- 📊 Sin monitoreo de integridad
- 🚫 No escalable para múltiples apps

### 🟢 DESPUÉS: Bind Mounts Empresariales

```yaml
# docker-compose.yml
services:
  db:
    volumes:
      - /opt/ecodisseny/data/postgres:/var/lib/postgresql/data # ✅ Ubicación explícita
      - /opt/ecodisseny/backups/postgres:/var/backups/postgresql # ✅ Backup automático
      - /opt/ecodisseny/config/postgres:/etc/postgresql/conf.d # ✅ Configuración externa
      - /opt/ecodisseny/logs/postgres:/var/log/postgresql # ✅ Logs centralizados

  web:
    volumes:
      - /opt/ecodisseny/data/static:/app/staticfiles # ✅ Archivos controlados
      - /opt/ecodisseny/data/media:/app/media # ✅ Media accesible
      - /opt/ecodisseny/logs/django:/app/logs # ✅ Logs aplicación

  redis:
    volumes:
      - /opt/ecodisseny/data/redis:/data # ✅ Cache persistente

  pgadmin:
    volumes:
      - /opt/ecodisseny/data/pgadmin:/var/lib/pgadmin # ✅ Configuración admin
```

**Beneficios obtenidos:**

- 📍 Ubicación conocida: `/opt/ecodisseny/`
- 💾 Backup automático cada 6 horas
- 🔧 Migración simple: copiar directorio
- 📊 Monitoreo continuo cada 15 minutos
- 🚀 Preparado para múltiples aplicaciones

---

## 🏗️ Arquitectura Final

### 📁 Estructura de Directorios

```
/opt/ecodisseny/
├── data/                           # 📊 DATOS PERSISTENTES
│   ├── postgres/                   # Base de datos PostgreSQL
│   │   ├── base/                   # Datos de las bases de datos
│   │   ├── pg_wal/                 # Write-Ahead Logs
│   │   └── postgresql.conf         # Configuración PostgreSQL
│   ├── redis/                      # Cache Redis (preparado para Oscar)
│   ├── media/                      # Archivos subidos Ecodisseny
│   │   └── pdfs_pressupostos/      # PDFs de presupuestos
│   ├── static/                     # Archivos estáticos Ecodisseny
│   ├── oscar/                      # 🚀 PREPARADO PARA OSCAR SHOP
│   │   ├── media/                  # Archivos Oscar Shop
│   │   └── static/                 # Estáticos Oscar Shop
│   └── pgadmin/                    # Configuración administrador DB
├── backups/                        # 💾 SISTEMA DE BACKUP
│   ├── postgres/                   # Backups base de datos
│   │   ├── ecodisseny_YYYYMMDD_HHMMSS.sql
│   │   ├── oscar_shop_YYYYMMDD_HHMMSS.sql
│   │   └── full_backup_YYYYMMDD_HHMMSS.sql
│   ├── daily/                      # Backups diarios comprimidos
│   │   ├── media_ecodisseny_*.tar.gz
│   │   ├── config_*.tar.gz
│   │   └── app_code_*.tar.gz
│   ├── weekly/                     # Backups semanales
│   └── monthly/                    # Backups mensuales
├── config/                         # ⚙️ CONFIGURACIÓN
│   ├── postgres/                   # Configuración PostgreSQL
│   │   ├── postgresql.conf         # Configuración optimizada
│   │   └── init-multiple-databases.sh
│   ├── nginx/                      # Configuración Nginx
│   │   └── ecodisseny.conf         # Virtual host con SSL
│   └── backup_config.conf          # Configuración backup
├── logs/                           # 📝 LOGS CENTRALIZADOS
│   ├── postgres/                   # Logs PostgreSQL
│   ├── django/                     # Logs Django/Gunicorn
│   │   ├── gunicorn_access.log
│   │   └── gunicorn_error.log
│   ├── oscar/                      # Logs Oscar Shop (preparado)
│   ├── nginx/                      # Logs Nginx
│   │   ├── access.log
│   │   └── error.log
│   ├── migration_*.log             # Logs de migración
│   └── backup_*.log                # Logs de backup
└── scripts/                        # 🔧 SCRIPTS DE ADMINISTRACIÓN
    ├── backup_completo.sh          # Backup completo manual
    ├── backup_incremental.sh       # Backup incremental
    ├── backup_semanal.sh           # Backup semanal
    ├── restore_backup.sh           # Restauración de backup
    ├── monitor_sistema.sh          # Monitoreo del sistema
    └── info_sistema.sh             # Información general
```

### 🐳 Servicios Docker

| Servicio    | Puerto           | Función           | Estado         |
| ----------- | ---------------- | ----------------- | -------------- |
| **db**      | 5432 (localhost) | PostgreSQL 15     | ✅ Funcionando |
| **web**     | 8000             | Django Ecodisseny | ✅ Funcionando |
| **redis**   | 6379 (localhost) | Cache y sesiones  | ✅ Funcionando |
| **pgadmin** | 8080 (localhost) | Administración DB | ✅ Funcionando |

---

## 🔄 Proceso de Migración Ejecutado

### Fase 1: 🔒 Backup de Seguridad

```bash
./migration_phase1_backup.sh
```

**Acciones realizadas:**

- ✅ Backup completo PostgreSQL (`pg_dumpall`)
- ✅ Backup individual base de datos Ecodisseny
- ✅ Backup volúmenes Docker completos (tar.gz)
- ✅ Backup configuración actual (docker-compose.yml, .env)
- ✅ Verificación integridad de todos los backups

**Archivos creados:**

- `/tmp/migration_backup_*/full_database.sql`
- `/tmp/migration_backup_*/ecodisseny_db.sql`
- `/tmp/migration_backup_*/postgres_volume.tar.gz`
- `/tmp/migration_backup_*/media_volume.tar.gz`

### Fase 2: 🏗️ Estructura de Directorios

```bash
./migration_phase2_structure.sh
```

**Acciones realizadas:**

- ✅ Creación estructura `/opt/ecodisseny/`
- ✅ Configuración permisos correctos:
  - PostgreSQL: `999:999`
  - Media/Static: `1000:1000`
  - pgAdmin: `5050:5050`
- ✅ Configuración PostgreSQL optimizada
- ✅ Archivos de log iniciales
- ✅ Configuración backup automático

### Fase 3: 🔄 Migración de Datos

```bash
./migration_phase3_migrate.sh
```

**Acciones realizadas:**

- ✅ Backup final pre-migración
- ✅ Parada graceful de servicios
- ✅ Migración datos PostgreSQL: volumen → `/opt/ecodisseny/data/postgres/`
- ✅ Migración archivos media: volumen → `/opt/ecodisseny/data/media/`
- ✅ Migración archivos static: volumen → `/opt/ecodisseny/data/static/`
- ✅ Ajuste permisos post-migración
- ✅ Verificación integridad datos migrados

### Fase 4: ⚙️ Nueva Configuración

```bash
./migration_phase4_config.sh
```

**Acciones realizadas:**

- ✅ Nuevo `docker-compose.yml` con bind mounts
- ✅ Variables de entorno actualizadas (`.env`)
- ✅ Configuración PostgreSQL para múltiples bases de datos
- ✅ Preparación servicios Redis y pgAdmin
- ✅ Configuración Nginx con logs estructurados

### Fase 5: 🧪 Pruebas y Validación

```bash
./migration_phase5_test.sh
```

**Acciones realizadas:**

- ✅ Inicio PostgreSQL con nueva configuración
- ✅ Verificación conectividad base de datos
- ✅ Inicio Redis y verificación funcionamiento
- ✅ Inicio aplicación web Django
- ✅ Pruebas funcionalidad (página principal, login)
- ✅ Inicio pgAdmin
- ✅ Verificación logs y archivos media/static

### Fase 6: 💾 Backups Automáticos

```bash
./migration_phase6_backup.sh
```

**Acciones realizadas:**

- ✅ Script backup completo con verificación
- ✅ Script backup incremental cada 6 horas
- ✅ Script backup semanal (domingos)
- ✅ Script restauración con verificación temporal
- ✅ Sistema monitoreo cada 15 minutos
- ✅ Configuración crontab automático
- ✅ Primer backup de prueba ejecutado

### Fase 7: 🧹 Finalización y Limpieza

```bash
./migration_phase7_cleanup.sh
```

**Acciones realizadas:**

- ✅ Limpieza volúmenes Docker antiguos (opcional)
- ✅ Documentación completa de migración
- ✅ Scripts información y monitoreo
- ✅ Aliases útiles en bash
- ✅ Verificación final del sistema

---

## 📊 Configuración Final

### Variables de Entorno (.env)

```properties
# Base de datos
DB_NAME=ecodisseny_db
DB_USER=ecodisseny_user
DB_PASSWORD=ecodisseny_password123
DB_HOST=db
DB_PORT=5432

# Persistencia empresarial
ECODISSENY_DATA_DIR=/opt/ecodisseny/data
ECODISSENY_BACKUP_DIR=/opt/ecodisseny/backups
ECODISSENY_LOG_DIR=/opt/ecodisseny/logs

# Redis
REDIS_URL=redis://redis:6379/0

# pgAdmin
PGADMIN_EMAIL=admin@ecodisseny.com
PGADMIN_PASSWORD=admin123

# Backup
BACKUP_RETENTION_DAYS=30
BACKUP_EMAIL_ALERTS=admin@ecodisseny.com
```

### Docker Compose Principal

```yaml
version: "3.8"

services:
  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: ecodisseny_db
      POSTGRES_USER: ecodisseny_user
      POSTGRES_PASSWORD: ecodisseny_password123
      POSTGRES_MULTIPLE_DATABASES: ecodisseny_db,oscar_shop
    volumes:
      - /opt/ecodisseny/data/postgres:/var/lib/postgresql/data
      - /opt/ecodisseny/backups/postgres:/var/backups/postgresql
      - /opt/ecodisseny/config/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
      - /opt/ecodisseny/logs/postgres:/var/log/postgresql
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ecodisseny_user -d ecodisseny_db"]
      interval: 30s
      timeout: 10s
      retries: 3
    command: postgres -c config_file=/etc/postgresql/postgresql.conf

  web:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - /opt/ecodisseny/data/static:/app/staticfiles
      - /opt/ecodisseny/data/media:/app/media
      - /opt/ecodisseny/logs/django:/app/logs
    depends_on:
      db:
        condition: service_healthy

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - /opt/ecodisseny/data/redis:/data
    command: redis-server --appendonly yes --maxmemory 512mb
    ports:
      - "127.0.0.1:6379:6379"

  pgadmin:
    image: dpage/pgadmin4:latest
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@ecodisseny.com
      PGADMIN_DEFAULT_PASSWORD: admin123
    volumes:
      - /opt/ecodisseny/data/pgadmin:/var/lib/pgadmin
    ports:
      - "127.0.0.1:8080:80"
```

---

## 💾 Sistema de Backup Automático

### ⏰ Programación Automática (Crontab)

```bash
# Backup completo diario a las 2:00 AM
0 2 * * * /opt/ecodisseny/scripts/backup_completo.sh

# Backup incremental cada 6 horas
0 */6 * * * /opt/ecodisseny/scripts/backup_incremental.sh

# Backup semanal (domingos a las 1:00 AM)
0 1 * * 0 /opt/ecodisseny/scripts/backup_semanal.sh

# Monitoreo cada 15 minutos
*/15 * * * * /opt/ecodisseny/scripts/monitor_sistema.sh
```

### 📋 Tipos de Backup

| Tipo            | Frecuencia         | Contenido           | Retención  |
| --------------- | ------------------ | ------------------- | ---------- |
| **Completo**    | Diario 2:00 AM     | BD + Media + Config | 30 días    |
| **Incremental** | Cada 6 horas       | Solo BD             | 24 backups |
| **Semanal**     | Domingos 1:00 AM   | Completo → weekly/  | 12 semanas |
| **Mensual**     | Primer domingo mes | Semanal → monthly/  | 12 meses   |

### 🔧 Scripts Disponibles

```bash
# Backup manual completo
/opt/ecodisseny/scripts/backup_completo.sh

# Backup incremental
/opt/ecodisseny/scripts/backup_incremental.sh

# Restaurar backup
/opt/ecodisseny/scripts/restore_backup.sh /path/to/backup.sql

# Monitoreo sistema
/opt/ecodisseny/scripts/monitor_sistema.sh

# Información general
/opt/ecodisseny/scripts/info_sistema.sh
```

---

## 🔍 Monitoreo y Mantenimiento

### 📊 Aliases Útiles

```bash
# Añadidos a /root/.bashrc
alias ecodisseny-status='/opt/ecodisseny/scripts/info_sistema.sh'
alias ecodisseny-logs='tail -f /opt/ecodisseny/logs/django/gunicorn_access.log'
alias ecodisseny-backup='/opt/ecodisseny/scripts/backup_completo.sh'
alias ecodisseny-monitor='/opt/ecodisseny/scripts/monitor_sistema.sh'
alias ecodisseny-cd='cd /root/ecodisseny_dj_pg'
```

### 🚨 Sistema de Alertas

El sistema monitorea automáticamente:

- **💾 Espacio en disco**: Alerta si > 85%
- **🐳 Estado contenedores**: Verifica todos los servicios
- **🗄️ Conectividad PostgreSQL**: Test cada 15 minutos
- **🌐 Aplicación web**: Verificación HTTP
- **💾 Backups**: Alerta si último backup > 25 horas
- **📝 Logs de error**: Cuenta errores en aplicación

### 📈 Métricas de Rendimiento

**Configuración PostgreSQL optimizada:**

```ini
# /opt/ecodisseny/config/postgres/postgresql.conf
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_segments = 32
autovacuum = on
```

---

## 🚀 Preparación Multi-App (Oscar Shop)

### 🛒 Arquitectura Preparada

La migración ha preparado la infraestructura para añadir **Django Oscar Shop**:

```yaml
# Futuro: Añadir Oscar Shop
oscar_shop:
  build: ./oscar_shop
  restart: unless-stopped
  ports:
    - "8001:8000" # Puerto diferente
  volumes:
    - /opt/ecodisseny/data/oscar/media:/app/media # Media separada
    - /opt/ecodisseny/data/oscar/static:/app/staticfiles # Static separada
    - /opt/ecodisseny/logs/oscar:/app/logs # Logs separados
  environment:
    - DB_HOST=db
    - DB_NAME=oscar_shop # Base de datos separada
    - REDIS_URL=redis://redis:6379/1 # DB Redis diferente
```

### 📊 Bases de Datos Múltiples

PostgreSQL configurado para múltiples aplicaciones:

- **ecodisseny_db**: Aplicación actual
- **oscar_shop**: Preparado para Django Oscar
- **Futuras apps**: Fácil añadir nuevas bases de datos

### 🔄 Shared Services

Servicios compartidos optimizados:

- **PostgreSQL**: Una instancia para todas las apps
- **Redis**: Múltiples bases de datos (0, 1, 2...)
- **pgAdmin**: Administración centralizada
- **Nginx**: Routing a múltiples aplicaciones

---

## ✅ Verificación Post-Migración

### 🧪 Tests Realizados

1. **✅ Conectividad PostgreSQL**: `pg_isready` exitoso
2. **✅ Aplicación web**: HTTP 200 en `/` y `/accounts/login/`
3. **✅ Redis**: `redis-cli ping` responde PONG
4. **✅ pgAdmin**: Interfaz web accesible en puerto 8080
5. **✅ Archivos media**: PDFs presupuestos disponibles
6. **✅ Archivos static**: CSS/JS servidos correctamente
7. **✅ Logs**: Escritura correcta en archivos centralizados
8. **✅ Backup**: Primer backup automático ejecutado
9. **✅ Monitoreo**: Sistema vigilancia funcionando

### 📊 Estado Actual del Sistema

```bash
🏢 ECODISSENY - INFORMACIÓN DEL SISTEMA
=======================================

📅 Fecha: 2025-08-21
🖥️ Servidor: vps-ecodisseny
👤 Usuario: root

🐳 SERVICIOS DOCKER
-------------------
✅ db (postgres:15) - Up 3 hours - Healthy
✅ web (ecodisseny_dj_pg_web) - Up 3 hours
✅ redis (redis:7-alpine) - Up 3 hours
✅ pgadmin (dpage/pgadmin4) - Up 3 hours

💾 ESTADO DE DATOS
------------------
📊 PostgreSQL: ✅ Conectado - Tamaño: 50MB - Tablas: 45
📁 Archivos Media: 3 archivos
📄 Archivos Static: 127 archivos

💽 ESPACIO EN DISCO
-------------------
/dev/sda1  72G  6.2G  66G  9% /opt/ecodisseny
📊 Tamaño /opt/ecodisseny: 145MB

💾 BACKUPS DISPONIBLES
----------------------
📊 Backups PostgreSQL: 3
📊 Backups Diarios: 2
📊 Último backup: ecodisseny_20250821_220000.sql

🌐 ACCESOS
----------
- Aplicación: http://localhost:8000
- pgAdmin: http://localhost:8080
- Dominio público: https://app.arasmu.net
```

---

## 🎯 Próximos Pasos

### 1. 🛒 Integración Django Oscar Shop

- Configurar nueva aplicación Django Oscar
- Añadir al docker-compose.yml
- Configurar base de datos `oscar_shop`
- Routing Nginx para múltiples apps

### 2. 🔐 Mejoras de Seguridad

- Certificados SSL automáticos (Certbot)
- Firewall específico para servicios
- Backup cifrado con GPG
- Autenticación 2FA para pgAdmin

### 3. 📊 Optimizaciones

- Monitoring con Prometheus/Grafana
- Cache Redis más avanzado
- CDN para archivos static
- Optimización consultas PostgreSQL

### 4. 🚀 DevOps

- CI/CD con GitHub Actions
- Staging environment
- Blue-green deployment
- Automated testing

---

## 📞 Soporte y Troubleshooting

### 🔧 Comandos de Diagnóstico

```bash
# Estado general
ecodisseny-status

# Logs en tiempo real
ecodisseny-logs

# Verificar servicios Docker
docker-compose ps

# Estado PostgreSQL
docker exec ecodisseny_dj_pg_db_1 pg_isready -U ecodisseny_user

# Conectar a PostgreSQL
docker exec -it ecodisseny_dj_pg_db_1 psql -U ecodisseny_user -d ecodisseny_db

# Ver espacio utilizado
du -sh /opt/ecodisseny/

# Últimos backups
ls -la /opt/ecodisseny/backups/postgres/ | tail -5

# Logs de error
grep ERROR /opt/ecodisseny/logs/django/*.log | tail -10
```

### 🚨 Procedimientos de Emergencia

#### Restaurar Base de Datos

```bash
# 1. Listar backups disponibles
ls -la /opt/ecodisseny/backups/postgres/

# 2. Restaurar backup específico
/opt/ecodisseny/scripts/restore_backup.sh /opt/ecodisseny/backups/postgres/ecodisseny_20250821_140000.sql

# 3. Verificar restauración
docker exec ecodisseny_dj_pg_db_1 psql -U ecodisseny_user -d ecodisseny_db -c "\dt"
```

#### Rollback Completo

```bash
# 1. Parar servicios actuales
docker-compose down

# 2. Restaurar configuración original
cp docker-compose.yml.pre-migration docker-compose.yml
cp .env.pre-migration .env

# 3. Restaurar volúmenes Docker (si existen)
docker volume create ecodisseny_dj_pg_postgres_data
# ... restaurar desde backup

# 4. Reiniciar con configuración original
docker-compose up -d
```

---

## 📋 Checklist de Validación

### ✅ Migración Completada

- [x] **Backup inicial creado y verificado**
- [x] **Estructura de directorios creada**
- [x] **Datos migrados sin pérdida**
- [x] **Nueva configuración funcionando**
- [x] **Todos los servicios operativos**
- [x] **Sistema backup automático activo**
- [x] **Monitoreo configurado**
- [x] **Documentación completa**
- [x] **Scripts de mantenimiento disponibles**
- [x] **Preparación multi-app realizada**

### 🎯 Objetivos Alcanzados

- [x] **Persistencia de datos garantizada**
- [x] **Ubicación de datos conocida y controlada**
- [x] **Sistema de backup robusto y automático**
- [x] **Escalabilidad para múltiples aplicaciones**
- [x] **Monitoreo y alertas funcionando**
- [x] **Facilidad de migración entre servidores**
- [x] **Procedures de recuperación documentados**
- [x] **Performance optimizado**

---

## 📚 Referencias y Documentación

### 📖 Documentos Relacionados

- `/opt/ecodisseny/MIGRATION_SUMMARY.md` - Resumen técnico
- `docs/dev/arquitectura-multi-app.md` - Arquitectura multi-aplicación
- `docs/dev/persistencia-datos.md` - Estrategia persistencia detallada
- `docs/dev/guia-completa-vps.md` - Guía deployment VPS

### 🔗 Enlaces Útiles

- [Docker Compose Volumes](https://docs.docker.com/compose/compose-file/#volumes)
- [PostgreSQL in Docker](https://hub.docker.com/_/postgres)
- [Django Oscar Documentation](https://django-oscar.readthedocs.io/)
- [Redis Configuration](https://redis.io/documentation)

---

**Migración completada exitosamente**: 21 de Agosto, 2025  
**Versión**: Ecodisseny Persistencia Empresarial v1.0  
**Estado**: ✅ Producción - Todos los sistemas operativos  
**Próximo hito**: 🛒 Integración Django Oscar Shop
