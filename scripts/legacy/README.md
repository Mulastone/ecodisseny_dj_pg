# Scripts Legacy (Archivados)

Estos scripts se conservaron solo por historial/consulta.
No son parte del flujo actual de despliegue ni backup.

Flujo vigente:
- `docker compose` (no `docker-compose` legacy)
- `README_DEPLOYMENT.md` como guia principal
- scripts activos en raiz:
  - `backup-db-gdrive.sh`
  - `backup-pdfs-gdrive.sh`
  - `backup-complete-gdrive.sh`
  - `restore-db-from-gdrive.sh`
  - `restore-pdfs-from-gdrive.sh`
  - `reset-base.sh`

Script archivado por riesgo alto en entorno no controlado:
- `reset_migrations.sh` (borra migraciones y puede recrear DB con `sudo`)

Usa scripts legacy solo si tienes un caso historico y sabes exactamente la infraestructura para la que fueron escritos.
