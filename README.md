# Ecodisseny Django

Aplicacion Django para la gestion interna de Ecodisseny. Incluye modulos para presupuestos, projectes, hores, maestros, documentacion y cuentas de usuario, con despliegue en Docker para desarrollo y produccion.

## Vista rapida

- `docker-compose.yml`: entorno de desarrollo local.
- `docker-compose.prod.yml`: entorno de produccion.
- `.env.dev`: variables para desarrollo.
- `.env.prod`: variables para produccion en VPS.
- `README_DEPLOYMENT.md`: guia operativa principal.
- `comandos.md`: chuleta rapida de comandos.

## Funcionalidades principales

- Gestion de presupuestos y lineas de presupuesto.
- Registro y seguimiento de horas.
- Catalogos maestros y perfiles de usuario.
- Documentacion interna y archivos asociados.
- Panel de administracion Django personalizado con Jazzmin.

## Requisitos

- Docker y Docker Compose.
- PostgreSQL (levantado por Compose en local y en produccion).
- Para envios y certificados en produccion: una cuenta de correo valida para Certbot.

## Desarrollo local

1. Copia o revisa `.env.dev`.
2. Arranca los servicios:

```bash
docker compose --env-file .env.dev up -d --build
```

3. Comprueba el estado:

```bash
docker compose --env-file .env.dev ps
docker compose --env-file .env.dev logs --tail=100 web
```

4. Si necesitas shell o tests:

```bash
docker compose --env-file .env.dev exec web python manage.py shell
docker compose --env-file .env.dev exec web python manage.py test
```

## Produccion en VPS

Usa siempre el compose de produccion y el archivo `.env.prod`:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

Notas importantes:

- En produccion no se cargan fixtures al arrancar.
- Si el VPS usa nginx del sistema, el servicio `web` publica `127.0.0.1:8000:8000` para permitir el proxy local.
- No uses `down -v` salvo que quieras borrar la base de datos y los volumenes.

## Variables de entorno

Minimas para produccion:

- `DOMAIN_NAME`
- `SERVER_IP`
- `DB_PASSWORD`
- `SECRET_KEY`
- `EMAIL`

El fichero `.env.prod` sirve como plantilla operativa del VPS.

## Backups y restauracion

Scripts disponibles:

- `backup-db-gdrive.sh`
- `backup-pdfs-gdrive.sh`
- `backup-complete-gdrive.sh`
- `restore-db-from-gdrive.sh`
- `restore-pdfs-from-gdrive.sh`
- `reset-base.sh`

La documentacion detallada esta en `README_DEPLOYMENT.md` y `SETUP_BACKUP_GDRIVE.md`.

## Documentacion util

- `README_DEPLOYMENT.md`: despliegue, backups, migracion y cutover.
- `comandos.md`: comandos operativos mas usados.
- `docs/`: documentacion funcional, tecnica y legacy.

## Estructura general

- `accounts/`: autentificacion y cuentas.
- `carregahores/`: carga de horas.
- `documentacion/`: gestion documental.
- `maestros/`: catalogos y perfiles.
- `pressupostos/`: presupuestos.
- `projectes/`: gestion de proyectos.
- `ecodisseny/`: settings, urls, wsgi y asgi.
- `templates/` y `static/`: vistas y recursos.

## Estado operativo

Este repositorio esta preparado para trabajar con:

- desarrollo local via Docker Compose
- produccion en VPS con `.env.prod`
- backups en Google Drive mediante `rclone`

Si quieres la guia paso a paso de operacion, usa `README_DEPLOYMENT.md`.

Contenido legacy archivado:
- `docs/legacy/`
- `scripts/legacy/`
