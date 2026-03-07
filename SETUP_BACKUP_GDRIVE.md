# Setup Google Drive Backup (rclone)

Guia de configuracion de `rclone` para usar los scripts:
- `backup-db-gdrive.sh`
- `backup-pdfs-gdrive.sh`
- `backup-complete-gdrive.sh`
- `restore-db-from-gdrive.sh`
- `restore-pdfs-from-gdrive.sh`

La operacion diaria y migracion VPS->VPS esta centralizada en `README_DEPLOYMENT.md`.

## 1. Instalar rclone

```bash
curl https://rclone.org/install.sh | sudo bash
rclone version
```

## 2. Configurar remote `gdrive:`

```bash
rclone config
```

Valores recomendados:
1. `n` (new remote)
2. name: `gdrive`
3. storage: `drive`
4. `client_id`: Enter
5. `client_secret`: Enter
6. `scope`: `1` (full access)
7. `root_folder_id`: Enter
8. `service_account_file`: Enter
9. advanced config: `n`
10. auto config:
- En PC local con navegador: `y`
- En VPS por SSH: `n` y completar URL/codigo manualmente
11. team drive: `n` (si no usas Google Workspace compartido)
12. confirmar con `y`

Verificar:
```bash
rclone listremotes
rclone lsd gdrive:
```

## 3. Estructura remota esperada

Los scripts usan por defecto:
- BBDD: `gdrive:ecodisseny-backups/database`
- PDFs latest: `gdrive:ecodisseny-backups/pdfs/latest`
- PDFs snapshots opcionales: `gdrive:ecodisseny-backups/pdfs/snapshots/*`

## 4. Prueba manual

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
./backup-db-gdrive.sh
./backup-pdfs-gdrive.sh
./backup-complete-gdrive.sh
```

## 5. Cron recomendado

```bash
crontab -e
```

Ejemplo diario 02:00:
```cron
0 2 * * * cd /opt/ecodisseny/ecodisseny_dj_pg && ./backup-complete-gdrive.sh
```

## 6. Restore rapido

Listar backups de BBDD:
```bash
./restore-db-from-gdrive.sh
```

Restaurar BBDD:
```bash
./restore-db-from-gdrive.sh all_databases_YYYYMMDD_HHMMSS.tar.gz
```

Restaurar PDFs:
```bash
./restore-pdfs-from-gdrive.sh
```
