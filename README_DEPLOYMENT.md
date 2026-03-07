# Ecodisseny: Operacion, Backup y Migracion (Dev + VPS)

Documento fuente unico para operar el proyecto en local y en VPS:
- deploy de desarrollo y produccion
- backup de base de datos y PDFs en Google Drive
- restauracion/migracion a otro VPS

## 1. Estructura recomendada

Repositorio en VPS:
```bash
/opt/ecodisseny/ecodisseny_dj_pg
```

Archivos clave:
- `docker-compose.yml` (dev)
- `docker-compose.prod.yml` (prod)
- `.env.dev` (dev)
- `.env.prod` (prod)

## 2. Variables de entorno

### 2.1 Base de produccion (`.env.prod`)
Partir de:
```bash
cp .env.example .env.prod
```

Minimos obligatorios:
- `DOMAIN_NAME`
- `SERVER_IP`
- `DB_PASSWORD`
- `SECRET_KEY`
- `EMAIL`

Opcionales de bootstrap:
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`
- `APP_ADMIN_USERNAME`
- `APP_ADMIN_PASSWORD`
- `VPS_SSH_PASSWORD`

### 2.2 Variables de scripts de backup/restore (opcionales)
Puedes definirlas en shell o en `.env.prod`:
```bash
# Compose objetivo (por defecto prod)
COMPOSE_FILE=docker-compose.prod.yml
ENV_FILE=.env.prod
DB_SERVICE=db

# Formato: db:user (separados por espacios)
DB_SPECS="ecodisseny_db:ecodisseny"

# Google Drive
GDRIVE_REMOTE=gdrive:ecodisseny-backups/database
GDRIVE_REMOTE_ROOT=gdrive:ecodisseny-backups/pdfs

# Retencion
RETENTION_DAYS=30
SNAPSHOT_RETENTION_DAYS=30

# PDFs
REMOTE_LATEST_DIR=latest
PDFS_CREATE_SNAPSHOT=false
```

## 3. Desarrollo local

```bash
cd /home/mulastone/proyectos/ecodisseny_dj_pg
docker compose --env-file .env.dev up -d --build
docker compose --env-file .env.dev ps
docker compose --env-file .env.dev logs --tail=100 web
```

## 4. Produccion en VPS (primera vez)

```bash
cd /opt/ecodisseny
git clone <repo-url> ecodisseny_dj_pg
cd ecodisseny_dj_pg
git checkout main
cp .env.example .env.prod
nano .env.prod

# Revisar dominio/certificados en nginx/default.conf
nano nginx/default.conf

docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.prod ps

docker compose -f docker-compose.prod.yml --env-file .env.prod run --rm certbot
docker compose -f docker-compose.prod.yml --env-file .env.prod restart nginx
```

## 5. Backups en Google Drive

Prerequisito: `rclone` configurado con remote `gdrive:`.

### 5.1 Backup BBDD
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./backup-db-gdrive.sh
```

### 5.2 Backup PDFs
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./backup-pdfs-gdrive.sh
```

### 5.3 Backup completo
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./backup-complete-gdrive.sh
```

### 5.4 Cron recomendado
```bash
crontab -e
```

Ejemplo diario 02:00:
```cron
0 2 * * * cd /opt/ecodisseny/ecodisseny_dj_pg && ./backup-complete-gdrive.sh
```

## 6. Migracion a otro VPS (BBDD + PDFs)

Objetivo: pasar datos del VPS origen al VPS destino usando Google Drive.

### 6.1 En VPS origen
1. Asegurar stack arriba en origen.
2. Ejecutar backup completo:
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./backup-complete-gdrive.sh
```
3. Verificar en Drive:
```bash
rclone ls gdrive:ecodisseny-backups/database | tail -n 5
rclone lsd gdrive:ecodisseny-backups/pdfs
```

### 6.2 En VPS destino (infra + app)
1. Clonar repo y preparar `.env.prod`.
2. Levantar stack:
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```
3. Configurar `rclone` en el destino con el mismo remote (`gdrive:`).

### 6.3 Restaurar BBDD en destino
1. Listar backups disponibles:
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./restore-db-from-gdrive.sh
```
2. Restaurar un archivo concreto:
```bash
./restore-db-from-gdrive.sh all_databases_YYYYMMDD_HHMMSS.tar.gz
```

Modo no interactivo:
```bash
AUTO_YES=true ./restore-db-from-gdrive.sh all_databases_YYYYMMDD_HHMMSS.tar.gz
```

### 6.4 Restaurar PDFs en destino
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./restore-pdfs-from-gdrive.sh
```

Si quieres otra ruta remota:
```bash
./restore-pdfs-from-gdrive.sh gdrive:ecodisseny-backups/pdfs/latest
```

### 6.5 Verificaciones post-migracion
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py check
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py showmigrations
curl -I http://localhost
```

Verificar manualmente:
- login y admin
- listado de documentacion
- apertura de un PDF historico
- listados de carga-horas y presupuestos

## 7. Actualizaciones de produccion

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
git checkout main
git pull origin main
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py collectstatic --noinput
```

### 7.1 Cuando el cambio incluye schema (migraciones)
Si un release trae cambios de modelos (como nuevos campos en `PressupostLinia`), usa este orden:

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
git checkout main
git pull origin main

# Backup preventivo antes de migrar
./backup-db-gdrive.sh

# Deploy + migracion
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py check
```

Verificacion recomendada:
- abrir formulario de Pressupost
- crear/editar una linea y revisar nuevos checks de calculo
- confirmar que guarda y lista sin errores

## 8. Reset a sistema base (sin backups)

Usar cuando quieras reiniciar datos a estado inicial (migraciones + fixtures), sin restaurar dump.

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./reset-base.sh
```

Notas:
- borra solo el volumen de base de datos del proyecto.
- mantiene codigo y archivos no ligados a la DB.
- carga fixtures base al final (puedes desactivarlo con `LOAD_FIXTURES=false`).

## 9. Rollback rapido

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
git log --oneline -n 5
git checkout <commit_estable>
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

## 10. Documentos secundarios

- `SETUP_BACKUP_GDRIVE.md`: configuracion detallada de rclone
- `comandos.md`: chuleta corta de comandos operativos

Este archivo (`README_DEPLOYMENT.md`) es la referencia principal.

## 11. Cron final en VPS origen (recomendado)

Objetivo: asegurar backups automaticos mientras el VPS origen siga activo.

1. Editar cron del usuario que ejecuta los scripts:
```bash
crontab -e
```

2. Ejemplo recomendado (backup completo diario a las 02:00):
```cron
0 2 * * * cd /opt/ecodisseny/ecodisseny_dj_pg && ./backup-complete-gdrive.sh >> /opt/ecodisseny/ecodisseny_dj_pg/logs/cron-backup.log 2>&1
```

3. Verificar cron:
```bash
crontab -l
tail -n 50 /opt/ecodisseny/ecodisseny_dj_pg/logs/cron-backup.log
```

Nota: cuando completes la migracion, desactiva este cron en origen para evitar ejecuciones duplicadas.

## 12. Runbook de cutover (ventana 15-30 min)

Objetivo: pasar trafico de VPS origen a VPS destino con riesgo controlado.

### 11.1 T-24h a T-1h (preparacion)
1. VPS destino desplegado y funcionando internamente.
2. `rclone` configurado en destino.
3. Prueba de restore realizada al menos una vez (BBDD + PDFs).
4. Reducir TTL DNS (ej. 300 segundos) si aplica.

### 11.2 Inicio de ventana (T0)
1. Avisar mantenimiento y bloquear cambios funcionales en origen (sin altas/ediciones).
2. Ejecutar backup final en origen:
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./backup-complete-gdrive.sh
```
3. Verificar que el backup final aparece en Google Drive:
```bash
rclone ls gdrive:ecodisseny-backups/database | tail -n 3
```

### 11.3 Restauracion en destino (T0+)
1. Restaurar BBDD:
```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./restore-db-from-gdrive.sh all_databases_YYYYMMDD_HHMMSS.tar.gz
```
2. Restaurar PDFs:
```bash
./restore-pdfs-from-gdrive.sh
```
3. Verificaciones tecnicas:
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py check
curl -I http://localhost
```

### 11.4 Validacion funcional (smoke)
1. Login admin.
2. Listado documentacion y apertura de PDF.
3. Vistas principales de carga-horas/presupuestos.
4. Confirmar que no hay errores 500 en logs:
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod logs --tail=200 web
docker compose -f docker-compose.prod.yml --env-file .env.prod logs --tail=200 nginx
```

### 11.5 Switch de trafico
1. Actualizar DNS o proxy/LB al VPS destino.
2. Confirmar respuesta desde dominio final:
```bash
curl -I https://tu-dominio
```
3. Monitorizar 15-30 min.

### 11.6 Cierre
1. Desactivar cron de backups en origen (si ya no sera primario).
2. Mantener VPS origen en modo standby 24-72h.
3. Documentar hora de corte, backup usado y resultado final.

## 13. Material legacy archivado

Los scripts antiguos quedaron movidos a:
- `scripts/legacy/`

La documentacion historica quedo en:
- `docs/legacy/`

No forman parte del flujo operativo actual (`docker compose` + `.env.prod` + scripts de backup/restore nuevos).
