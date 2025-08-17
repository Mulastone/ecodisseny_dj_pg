# ⚙️ Configuración Inicial del Sistema

Como administrador de Ecodisseny, esta guía te ayudará a configurar el sistema desde cero y establecer las bases para un funcionamiento óptimo.

## 🎯 Objetivos de la Configuración

Al completar esta guía tendrás:
- ✅ **Sistema base configurado** correctamente
- ✅ **Datos maestros** establecidos (recursos, ubicaciones, tareas)
- ✅ **Usuarios y permisos** configurados
- ✅ **Configuración de seguridad** aplicada
- ✅ **Backups** automatizados

## 🚀 Primer Acceso como Administrador

### **1. Acceso al Panel de Administración**

```bash
URL: http://tudominio.com/admin/
Usuario: mulastone
Contraseña: Santom@E14
```

### **2. Dashboard de Administración**

El panel de Django Admin te proporciona:
- 📊 **Vista general** del sistema
- 👥 **Gestión de usuarios** y grupos
- 🔧 **Configuración** de aplicaciones
- 📋 **Datos maestros** (recursos, ubicaciones, etc.)
- 🔐 **Permisos** y seguridad

## 🏗️ Configuración de Datos Maestros

### **🏢 1. Configurar Recursos (Personal)**

Los recursos representan las personas que trabajarán en proyectos.

#### **Acceder a Recursos**
1. **Admin Panel** → **Maestros** → **Recursos**
2. **"Añadir Recurso"**

#### **Campos Obligatorios**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Nombre** | Nombre completo | "María García López" |
| **Tipo de Recurso** | Categoría profesional | "Arquitecto", "Ingeniero", "Operario" |
| **Código** | Identificador único | "MAR001" |
| **Activo** | Si está disponible | ✅ Sí |

#### **Campos Opcionales**
- **Email**: Contacto directo
- **Teléfono**: Número de contacto
- **Especialidad**: Área específica de trabajo
- **Fecha de alta**: Cuándo se incorporó

#### **💡 Buenas Prácticas para Recursos**

```
Nomenclatura de códigos:
- Primeras 3 letras del nombre + número
- MAR001, JUA002, PED003, etc.

Tipos de recurso estándar:
- Arquitecto
- Ingeniero
- Jefe de Obra
- Operario Especializado
- Operario General
- Administrativo
```

### **📍 2. Configurar Ubicaciones**

#### **Parroquias de Andorra**
El sistema viene preconfigurado con:
- Andorra la Vella
- Escaldes-Engordany
- Encamp
- La Massana
- Ordino
- Sant Julià de Lòria
- Canillo

#### **Añadir Nuevas Ubicaciones**
1. **Admin Panel** → **Maestros** → **Ubicaciones**
2. **"Añadir Ubicación"**
3. **Completar datos**:
   - Nombre de la ubicación
   - Parroquia padre (si aplica)
   - Código postal
   - Coordenadas (opcional)

### **🎯 3. Configurar Tareas y Trabajos**

#### **Tipos de Trabajo**
Configura las categorías principales:
- **Arquitectura**: Diseño, planos, supervisión
- **Obra Civil**: Construcción, reformas
- **Instalaciones**: Electricidad, fontanería, climatización
- **Acabados**: Pintura, pavimentos, carpintería

#### **Tareas Específicas**
Para cada tipo de trabajo, define tareas:
```
Arquitectura:
- Levantamiento topográfico
- Diseño de planos
- Dirección de obra
- Supervisión de calidad

Obra Civil:
- Demolición
- Cimentación
- Estructura
- Albañilería
```

### **🚗 4. Configurar Desplazamientos**

#### **Matriz de Distancias**
El sistema calcula automáticamente los costes de desplazamiento:

1. **Admin Panel** → **Maestros** → **Desplazamientos**
2. **Configurar distancias** entre ubicaciones
3. **Establecer tarifas** por kilómetro
4. **Definir tiempo** de desplazamiento

## 👥 Gestión de Usuarios

### **🔐 1. Crear Usuarios del Sistema**

#### **Proceso de Creación**
1. **Admin Panel** → **Autenticación** → **Usuarios**
2. **"Añadir Usuario"**
3. **Datos básicos**:
   - Username (nombre de usuario)
   - Email
   - Contraseña temporal
   - Nombre y apellidos

#### **4. Asignar Permisos**

**Niveles de acceso**:

| Nivel | Descripción | Permisos |
|-------|-------------|----------|
| **Superusuario** | Acceso total | Todo el sistema |
| **Staff** | Administrador | Panel admin + aplicación |
| **Usuario Normal** | Solo aplicación | Crear proyectos, registrar horas |
| **Solo Lectura** | Consultar datos | Ver reportes únicamente |

#### **Configurar Permisos Específicos**
```
Permisos por módulo:
✅ Proyectos: Crear, editar, eliminar, ver
✅ Presupuestos: Crear, editar, eliminar, ver, exportar PDF
✅ Horas: Registrar, editar propias, ver todas
✅ Reportes: Ver básicos, ver avanzados, exportar
✅ Maestros: Ver, editar (solo administradores)
```

### **🔗 2. Vincular Usuarios con Recursos**

**Cada usuario debe tener un perfil asociado**:

1. **Admin Panel** → **Carga Horas** → **Perfiles de Usuario**
2. **"Añadir Perfil"**
3. **Vincular**:
   - Usuario del sistema
   - Recurso (persona física)
   - Fecha de asignación

## 🔒 Configuración de Seguridad

### **🛡️ 1. Configuración Django**

#### **Variables de Entorno Críticas**
```bash
# .env (NUNCA subir a Git)
SECRET_KEY=clave_super_secreta_y_larga_aqui
DEBUG=False  # SIEMPRE False en producción
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
```

#### **Generar SECRET_KEY Segura**
```python
# En el VPS, ejecutar:
docker-compose exec web python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

### **🔐 2. Políticas de Contraseñas**

#### **Configuración Recomendada**
```python
# En settings.py (ya configurado)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

#### **Forzar Cambio de Contraseña**
```python
# Para usuarios nuevos
user.set_password('contraseña_temporal')
user.save()
# Informar al usuario que debe cambiarla en el primer acceso
```

### **🔄 3. Backup y Recuperación**

#### **Configurar Backups Automáticos**
```bash
# Crear script de backup
nano /home/ecodisseny/backup.sh

#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ecodisseny/backups"
mkdir -p $BACKUP_DIR

# Backup de base de datos
docker-compose exec -T db pg_dump -U ecodisseny ecodisseny_db > $BACKUP_DIR/db_$DATE.sql

# Backup de archivos media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Limpiar backups antiguos (mantener 30 días)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completado: $DATE"
```

#### **Programar en Cron**
```bash
# Añadir a crontab (ejecutar cada día a las 2:00 AM)
crontab -e
0 2 * * * /home/ecodisseny/backup.sh >> /var/log/ecodisseny_backup.log 2>&1
```

## 📊 Configuración del Sistema

### **⚙️ 1. Configuración General**

#### **Parámetros del Sistema**
1. **Admin Panel** → **Sitios** → **Sitios**
2. **Configurar**:
   - Nombre del sitio: "Ecodisseny - Gestión de Proyectos"
   - Dominio: "tudominio.com"

### **📧 2. Configuración de Email**

#### **SMTP Configuration**
```python
# En .env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@tudominio.com
EMAIL_HOST_PASSWORD=tu_app_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@tudominio.com
```

#### **Verificar Configuración**
```python
# Test desde Django shell
docker-compose exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Mensaje de prueba', 'from@email.com', ['to@email.com'])
```

### **📱 3. Configuración de Notificaciones**

#### **Tipos de Notificaciones**
- ✅ **Proyectos próximos a vencer**
- ✅ **Presupuestos sin respuesta**
- ✅ **Usuarios inactivos**
- ✅ **Errores del sistema**

## 🔍 Monitoreo y Mantenimiento

### **📊 1. Dashboard de Administración**

#### **Métricas Clave a Monitorear**
- 👥 **Usuarios activos** diarios/semanales
- 🏗️ **Proyectos creados** por período
- ⏱️ **Horas registradas** por recurso
- 💰 **Presupuestos generados**
- 🚨 **Errores** y excepciones

### **📋 2. Logs del Sistema**

#### **Ubicaciones de Logs**
```bash
# Logs de Django
docker-compose logs web

# Logs de PostgreSQL
docker-compose logs db

# Logs de Nginx (en producción)
docker-compose -f docker-compose.prod.yml logs nginx

# Logs del sistema
tail -f /var/log/syslog
```

### **🔧 3. Mantenimiento Preventivo**

#### **Tareas Semanales**
- ✅ **Revisar logs** de errores
- ✅ **Verificar backups** funcionando
- ✅ **Comprobar espacio** en disco
- ✅ **Actualizar estadísticas** de BD

#### **Tareas Mensuales**
- ✅ **Limpiar archivos** temporales
- ✅ **Optimizar base de datos**
- ✅ **Revisar usuarios** inactivos
- ✅ **Actualizar documentación**

## 🆘 Resolución de Problemas

### **❓ "Los usuarios no pueden acceder"**

**Diagnóstico**:
```bash
# Verificar servicios
docker-compose ps

# Verificar logs
docker-compose logs web

# Verificar configuración
docker-compose exec web python manage.py check
```

### **❓ "La aplicación va lenta"**

**Optimizaciones**:
```bash
# Verificar uso de recursos
docker stats

# Optimizar base de datos
docker-compose exec db psql -U ecodisseny ecodisseny_db -c "VACUUM ANALYZE;"

# Verificar índices
docker-compose exec web python manage.py dbshell
```

### **❓ "Error al generar PDFs"**

**Soluciones**:
```bash
# Verificar dependencias WeasyPrint
docker-compose exec web python -c "import weasyprint; print('OK')"

# Verificar permisos de media
docker-compose exec web ls -la /app/media/

# Regenerar contenedor si es necesario
docker-compose build --no-cache web
```

## 📞 Soporte Técnico

### **🆘 Contacto de Emergencia**
- **Email**: admin@ecodisseny.com
- **Telegram**: @ecodisseny_support
- **Teléfono**: +376 XXX XXX (24/7 para emergencias)

### **📚 Documentación Avanzada**
- [👥 Gestión de Usuarios](usuarios.md) - Permisos y roles detallados
- [🏗️ Datos Maestros](datos-maestros.md) - Configuración avanzada
- [🔐 Seguridad](seguridad.md) - Hardening y mejores prácticas
- [📊 Mantenimiento](mantenimiento.md) - Rutinas de mantenimiento

---

*⚡ **Siguiente paso**: Configurar [usuarios y permisos](usuarios.md) en detalle.*
