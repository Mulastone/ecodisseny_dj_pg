# Comandos Operativos (chuleta)

Referencia completa: `README_DEPLOYMENT.md`.

## Dev

```bash
cd /home/mulastone/proyectos/ecodisseny_dj_pg
docker compose --env-file .env.dev up -d --build
docker compose --env-file .env.dev ps
docker compose --env-file .env.dev logs --tail=100 web
docker compose --env-file .env.dev exec web python manage.py test
```

## Prod VPS

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
docker compose -f docker-compose.prod.yml --env-file .env.prod logs --tail=150 web
```

## Backup

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./backup-db-gdrive.sh
./backup-pdfs-gdrive.sh
./backup-complete-gdrive.sh
```

## Reset base (sin restore)

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./reset-base.sh
```

## Restore / Migracion

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./restore-db-from-gdrive.sh
./restore-db-from-gdrive.sh all_databases_YYYYMMDD_HHMMSS.tar.gz
./restore-pdfs-from-gdrive.sh
```

## Deploy update

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
git checkout main
git pull origin main
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py collectstatic --noinput
```

## Alta Intern/Colaborador (SOP)

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web \
python manage.py crear_recurso_usuari \
  --username <usuario> \
  --first_name <nombre> \
  --email <correo> \
  --password '<password_temporal>' \
  --recurso_name <nombre_recurso> \
  --tipo_recurso Intern
```
