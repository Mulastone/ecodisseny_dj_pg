# 🚨 Troubleshooting - Resolución de Problemas

Guía completa para diagnosticar y resolver los problemas más comunes en Ecodisseny.

## 🎯 Diagnóstico Rápido

### **⚡ Lista de Verificación Inicial**

Cuando algo no funciona, sigue estos pasos en orden:

1. **🔍 Identificar el problema**

   - ¿Qué estaba intentando hacer?
   - ¿Cuándo empezó el problema?
   - ¿Hay mensajes de error?

2. **📊 Verificar servicios básicos**

   ```bash
   # Estado de contenedores
   docker-compose ps

   # Logs recientes
   docker-compose logs --tail=50
   ```

3. **🌐 Verificar conectividad**

   - ¿La aplicación responde en http://localhost:8000?
   - ¿El admin responde en /admin/?
   - ¿La base de datos está accesible?

4. **👤 Verificar permisos de usuario**
   - ¿El usuario tiene permisos adecuados?
   - ¿Está en el grupo correcto?
   - ¿Está activo?

## 🔧 Problemas de Acceso y Autenticación

### **❌ "No puedo acceder al sistema"**

#### **Síntomas**:

- Página de login no aparece
- Error 500 en /accounts/login/
- "Connection refused"

#### **Diagnóstico**:

```bash
# 1. Verificar servicios ejecutándose
docker-compose ps
# Resultado esperado: web y db "Up"

# 2. Verificar puertos
netstat -tlnp | grep :8000
# Resultado esperado: :::8000 LISTEN

# 3. Verificar logs de la aplicación
docker-compose logs web --tail=20
```

#### **Soluciones**:

**Si servicios no están ejecutándose**:

```bash
docker-compose up -d
```

**Si hay error en la aplicación**:

```bash
# Ver error específico
docker-compose logs web

# Reiniciar servicios
docker-compose restart

# Si persiste, reconstruir
docker-compose down
docker-compose up --build
```

### **❌ "Credenciales incorrectas"**

#### **Síntomas**:

- "Please enter a correct username and password"
- Usuario no puede iniciar sesión

#### **Diagnóstico**:

```bash
# Verificar usuario existe y está activo
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='usuario_problema')
    print(f'Usuario existe: {user.username}')
    print(f'Activo: {user.is_active}')
    print(f'Staff: {user.is_staff}')
    print(f'Último acceso: {user.last_login}')
except User.DoesNotExist:
    print('Usuario NO existe')
"
```

#### **Soluciones**:

**Resetear contraseña**:

```bash
docker-compose exec web python manage.py changepassword usuario_problema
```

**Activar usuario desactivado**:

```bash
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='usuario_problema')
user.is_active = True
user.save()
print('Usuario activado')
"
```

### **❌ "No tengo permisos para ver esta página"**

#### **Síntomas**:

- Error 403 Forbidden
- "You don't have permission to access this page"

#### **Diagnóstico**:

```bash
# Verificar permisos del usuario
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='usuario_problema')
print(f'Grupos: {[g.name for g in user.groups.all()]}')
print(f'Es staff: {user.is_staff}')
print(f'Es superuser: {user.is_superuser}')
"
```

#### **Soluciones**:

**Asignar grupo correcto**:

```bash
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.get(username='usuario_problema')
group = Group.objects.get(name='Usuarios Normales')
user.groups.add(group)
print('Grupo asignado')
"
```

## 🗄️ Problemas de Base de Datos

### **❌ "Error de conexión a la base de datos"**

#### **Síntomas**:

- "could not connect to server"
- "connection to database failed"
- La aplicación web no inicia

#### **Diagnóstico**:

```bash
# 1. Verificar contenedor de BD
docker-compose ps db

# 2. Verificar logs de PostgreSQL
docker-compose logs db --tail=20

# 3. Intentar conexión manual
docker-compose exec db psql -U ecodisseny ecodisseny_db -c "SELECT 1;"
```

#### **Soluciones**:

**Si el contenedor no está ejecutándose**:

```bash
docker-compose up -d db
```

**Si hay errores en los logs**:

```bash
# Reiniciar base de datos
docker-compose restart db

# Ver espacio en disco
df -h

# Si no hay espacio, limpiar
docker system prune -a
```

**Si los datos están corruptos**:

```bash
# ⚠️ CUIDADO: Esto borra todos los datos
docker-compose down
docker volume rm ecodisseny_dj_pg_postgres_data
docker-compose up -d
# Luego restaurar desde backup
```

### **❌ "Migraciones pendientes"**

#### **Síntomas**:

- "You have X unapplied migration(s)"
- Error al acceder a ciertas páginas

#### **Diagnóstico**:

```bash
# Verificar migraciones pendientes
docker-compose exec web python manage.py showmigrations
```

#### **Soluciones**:

```bash
# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Si hay conflictos, verificar
docker-compose exec web python manage.py migrate --plan

# En caso extremo, recrear migraciones
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## 📄 Problemas con PDFs

### **❌ "Error al generar PDF"**

#### **Síntomas**:

- "WeasyPrint error"
- PDF en blanco o incompleto
- Timeout al generar

#### **Diagnóstico**:

```bash
# 1. Verificar WeasyPrint funciona
docker-compose exec web python -c "
import weasyprint
print('WeasyPrint OK')
html = '<html><body><h1>Test</h1></body></html>'
pdf = weasyprint.HTML(string=html).write_pdf()
print(f'PDF generado: {len(pdf)} bytes')
"

# 2. Verificar permisos de media
docker-compose exec web ls -la /app/media/pdfs_pressupostos/

# 3. Verificar espacio en disco
docker-compose exec web df -h /app/media/
```

#### **Soluciones**:

**Problema de permisos**:

```bash
# Corregir permisos
docker-compose exec web chown -R ecodisseny:ecodisseny /app/media/
```

**Problema de dependencias**:

```bash
# Reconstruir contenedor
docker-compose build --no-cache web
docker-compose up -d web
```

**Problema de espacio**:

```bash
# Limpiar archivos antiguos
docker-compose exec web find /app/media/pdfs_pressupostos/ -name "*.pdf" -mtime +30 -delete
```

## 🔄 Problemas de Rendimiento

### **❌ "La aplicación va muy lenta"**

#### **Síntomas**:

- Páginas tardan más de 5 segundos en cargar
- Timeouts frecuentes
- Alta carga de CPU/memoria

#### **Diagnóstico**:

```bash
# 1. Verificar uso de recursos
docker stats

# 2. Verificar procesos en la BD
docker-compose exec db psql -U ecodisseny ecodisseny_db -c "
SELECT pid, usename, application_name, state, query_start, query
FROM pg_stat_activity
WHERE state = 'active' AND query NOT LIKE '%pg_stat_activity%';
"

# 3. Verificar logs de queries lentas
docker-compose logs web | grep -i "slow"
```

#### **Soluciones**:

**Optimizar base de datos**:

```bash
# Actualizar estadísticas
docker-compose exec db psql -U ecodisseny ecodisseny_db -c "VACUUM ANALYZE;"

# Reindexar si es necesario
docker-compose exec db psql -U ecodisseny ecodisseny_db -c "REINDEX DATABASE ecodisseny_db;"
```

**Aumentar recursos**:

```bash
# En docker-compose.yml, añadir:
services:
  web:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
  db:
    deploy:
      resources:
        limits:
          memory: 1G
```

### **❌ "Muchos archivos en media/"**

#### **Síntomas**:

- Disco lleno
- Búsquedas lentas
- Backup tardando mucho

#### **Soluciones**:

```bash
# Script de limpieza de archivos antiguos
docker-compose exec web bash -c "
find /app/media/pdfs_pressupostos/ -name '*.pdf' -mtime +90 -print
find /app/media/pdfs_pressupostos/ -name '*.pdf' -mtime +90 -delete
echo 'Archivos antiguos eliminados'
"

# Comprimir archivos antiguos
docker-compose exec web bash -c "
find /app/media/ -name '*.pdf' -mtime +30 -mtime -90 -exec gzip {} \;
"
```

## 🔒 Problemas de Seguridad

### **❌ "Intentos de acceso no autorizados"**

#### **Síntomas**:

- Muchos intentos de login fallidos en logs
- IPs sospechosas accediendo
- Usuarios reportan cuentas comprometidas

#### **Diagnóstico**:

```bash
# Verificar intentos fallidos recientes
docker-compose logs web | grep -i "invalid\|failed\|unauthorized" | tail -20

# Verificar accesos recientes
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

recent_logins = User.objects.filter(
    last_login__gte=timezone.now() - timedelta(hours=24)
).order_by('-last_login')

for user in recent_logins:
    print(f'{user.username}: {user.last_login}')
"
```

#### **Soluciones**:

**Medidas inmediatas**:

```bash
# Desactivar usuarios comprometidos
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='usuario_comprometido')
user.is_active = False
user.save()
print('Usuario desactivado')
"

# Forzar cambio de contraseñas
docker-compose exec web python manage.py changepassword usuario_comprometido
```

**Configurar firewall (en VPS)**:

```bash
# Bloquear IP específica
sudo ufw deny from 192.168.1.100

# Limitar conexiones SSH
sudo ufw limit ssh

# Solo permitir HTTPS
sudo ufw allow 443
sudo ufw deny 80
```

## 🐳 Problemas Docker

### **❌ "Contenedores no inician"**

#### **Síntomas**:

- `docker-compose up` falla
- Contenedores en estado "Exited"
- Errores de construcción

#### **Diagnóstico**:

```bash
# Ver estado detallado
docker-compose ps

# Ver logs de construcción
docker-compose build

# Ver logs de ejecución
docker-compose logs
```

#### **Soluciones**:

**Limpiar y reconstruir**:

```bash
# Parar y limpiar
docker-compose down
docker system prune -a

# Reconstruir desde cero
docker-compose build --no-cache
docker-compose up -d
```

**Problemas de espacio**:

```bash
# Verificar espacio
df -h

# Limpiar imágenes no usadas
docker image prune -a

# Limpiar volúmenes no usados
docker volume prune
```

### **❌ "Volúmenes corruptos"**

#### **Síntomas**:

- Datos perdidos entre reinicios
- Errores de permisos en archivos
- Base de datos no inicia

#### **Soluciones**:

**⚠️ CUIDADO: Estas operaciones borran datos**

```bash
# Backup primero
docker-compose exec db pg_dump -U ecodisseny ecodisseny_db > backup_emergency.sql

# Recrear volúmenes
docker-compose down
docker volume rm ecodisseny_dj_pg_postgres_data
docker volume rm ecodisseny_dj_pg_media_files
docker-compose up -d

# Restaurar datos
cat backup_emergency.sql | docker-compose exec -T db psql -U ecodisseny ecodisseny_db
```

## 📊 Herramientas de Diagnóstico

### **🔍 Script de Health Check**

```bash
#!/bin/bash
# health_check.sh

echo "=== ECODISSENY HEALTH CHECK ==="
echo "Fecha: $(date)"
echo

# 1. Estado de contenedores
echo "1. CONTENEDORES:"
docker-compose ps
echo

# 2. Uso de recursos
echo "2. RECURSOS:"
docker stats --no-stream
echo

# 3. Espacio en disco
echo "3. ESPACIO EN DISCO:"
df -h
echo

# 4. Conectividad de BD
echo "4. BASE DE DATOS:"
docker-compose exec -T db psql -U ecodisseny ecodisseny_db -c "SELECT 'BD OK' as status;" 2>/dev/null || echo "BD ERROR"
echo

# 5. Aplicación web
echo "5. APLICACIÓN WEB:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 || echo "WEB ERROR"
echo

# 6. Logs recientes con errores
echo "6. ERRORES RECIENTES:"
docker-compose logs --since="1h" | grep -i error | tail -5
echo

echo "=== FIN HEALTH CHECK ==="
```

### **📋 Commands útiles para administradores**

```bash
# Ver todos los usuarios activos
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
for u in User.objects.filter(is_active=True):
    print(f'{u.username:<15} {u.email:<30} {u.last_login}')
"

# Estadísticas generales
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
from projectes.models import Projecte
from pressupostos.models import Pressupost
from carregahores.models import RegistreHores

print(f'Usuarios: {User.objects.count()}')
print(f'Proyectos: {Projecte.objects.count()}')
print(f'Presupuestos: {Pressupost.objects.count()}')
print(f'Registros de horas: {RegistreHores.objects.count()}')
"

# Backup rápido
docker-compose exec db pg_dump -U ecodisseny ecodisseny_db | gzip > backup_$(date +%Y%m%d_%H%M).sql.gz
```

## 📞 Cuándo Contactar Soporte

### **🚨 Contacta INMEDIATAMENTE si**:

- 🔒 **Sospecha de brecha de seguridad**
- 💾 **Pérdida de datos** críticos
- 🌐 **Sistema completamente inaccesible** por más de 30 minutos
- 🔥 **Errores que afectan** a múltiples usuarios

### **📧 Contacta en horario laboral si**:

- 📊 **Reportes funcionan mal**
- 🎨 **Problemas de interface**
- ⚡ **Rendimiento degradado**
- ❓ **Dudas de configuración**

### **📝 Información a incluir**:

1. **Descripción del problema**
2. **Pasos para reproducir**
3. **Logs relevantes** (últimas 20 líneas)
4. **Usuarios afectados**
5. **Urgencia** (alta/media/baja)

### **📬 Canales de Contacto**:

- **🚨 Emergencias**: +376 XXX XXX
- **📧 Email**: soporte@ecodisseny.com
- **💬 Chat**: Botón de ayuda en la aplicación
- **📝 Tickets**: https://soporte.ecodisseny.com

---

_💡 **Recuerda**: Antes de contactar soporte, intenta los pasos básicos de diagnóstico. Esto acelera la resolución._
