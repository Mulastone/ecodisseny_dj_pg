# 🔐 Seguridad del Sistema

La seguridad es un aspecto crítico en Ecodisseny. Esta guía cubre la configuración de permisos, autenticación y mejores prácticas de seguridad.

## 👥 **Gestión de Permisos**

### 🔑 **Niveles de Usuario**

#### **Administrador**

- Acceso completo al sistema
- Gestión de usuarios y permisos
- Configuración del sistema
- Acceso a datos sensibles

#### **Usuario Estándar**

- Carga de horas trabajadas
- Visualización de proyectos asignados
- Acceso limitado a reportes

#### **Solo Lectura**

- Visualización de información
- Sin capacidad de modificación
- Acceso a reportes básicos

### 🛡️ **Configuración de Permisos**

#### Asignación de Roles

```
1. Ir a Admin > Usuarios > Grupos
2. Crear o seleccionar grupo
3. Asignar permisos específicos:
   - Lectura (view)
   - Escritura (add, change)
   - Eliminación (delete)
4. Guardar configuración
```

#### Permisos por Módulo

```
📊 Proyectos:
- admin: CRUD completo
- user: Solo lectura de asignados

💰 Presupuestos:
- admin: CRUD completo
- user: Sin acceso

⏱️ Carga de Horas:
- admin: CRUD completo
- user: Crear y editar propias

🏗️ Maestros:
- admin: CRUD completo
- user: Solo lectura
```

## 🔒 **Autenticación**

### 🔐 **Configuración de Contraseñas**

#### Políticas de Contraseñas

```python
# Configuración en settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8,}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

#### Requisitos de Contraseña

- **Mínimo 8 caracteres**
- **Combinación de mayúsculas y minúsculas**
- **Al menos un número**
- **Caracteres especiales recomendados**

### 🕐 **Sesiones**

#### Configuración de Sesiones

```python
# Duración de sesión (segundos)
SESSION_COOKIE_AGE = 3600  # 1 hora

# Expirar sesión al cerrar navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Seguridad de cookies
SESSION_COOKIE_SECURE = True  # Solo HTTPS
SESSION_COOKIE_HTTPONLY = True  # No JavaScript
```

#### Gestión de Sesiones Activas

```
1. Admin > Sesiones
2. Ver sesiones activas
3. Revocar sesiones sospechosas
4. Monitorear accesos
```

## 🌐 **Seguridad de Red**

### 🔥 **Firewall y Acceso**

#### Configuración de Firewall

```bash
# Permitir solo puertos necesarios
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 22/tcp   # SSH (restringido)

# Denegar todo lo demás
ufw default deny incoming
ufw default allow outgoing
```

#### Restricción de IP

```python
# En settings.py para restringir admin
ALLOWED_HOSTS = ['tu-dominio.com', '192.168.1.100']

# Middleware de IP whitelist para admin
ADMIN_IP_WHITELIST = ['192.168.1.0/24']
```

### 🔐 **HTTPS/SSL**

#### Configuración SSL

```nginx
server {
    listen 443 ssl;
    server_name tu-dominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
}
```

## 📊 **Auditoría y Monitoreo**

### 📝 **Logs de Seguridad**

#### Configuración de Logging

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/ecodisseny/security.log',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
        },
    },
}
```

#### Eventos a Monitorear

- Intentos de login fallidos
- Accesos administrativos
- Cambios en permisos
- Modificaciones de datos críticos

### 🚨 **Alertas de Seguridad**

#### Configuración de Alertas

```
1. Admin > Configuración > Alertas
2. Definir umbrales:
   - 5 login fallidos = Bloqueo temporal
   - Acceso fuera de horario = Notificación
   - Cambios masivos = Revisión manual
```

## 🔄 **Copias de Seguridad**

### 💾 **Backup de Datos**

#### Backup Automático

```bash
#!/bin/bash
# Script de backup diario
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/ecodisseny"

# Backup de base de datos
pg_dump ecodisseny_db > $BACKUP_DIR/db_$DATE.sql

# Backup de archivos
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /app/media/
```

#### Verificación de Backups

```
1. Verificar integridad de archivos
2. Probar restauración en entorno test
3. Documentar proceso de recuperación
4. Mantener copias offsite
```

## 🛡️ **Mejores Prácticas**

### ✅ **Recomendaciones de Seguridad**

#### Para Administradores

- Usar autenticación de dos factores
- Revisar logs regularmente
- Mantener software actualizado
- Realizar auditorías de permisos

#### Para Usuarios

- Cambiar contraseñas regularmente
- No compartir credenciales
- Cerrar sesión al terminar
- Reportar actividad sospechosa

### 🔍 **Auditorías Regulares**

#### Checklist Mensual

- [ ] Revisar usuarios activos
- [ ] Verificar permisos asignados
- [ ] Analizar logs de acceso
- [ ] Comprobar backups
- [ ] Actualizar software de seguridad

## 🆘 **Incidentes de Seguridad**

### 🚨 **Protocolo de Respuesta**

#### En caso de brecha de seguridad:

```
1. INMEDIATO:
   - Aislar sistema afectado
   - Cambiar credenciales comprometidas
   - Notificar al equipo de TI

2. INVESTIGACIÓN:
   - Analizar logs de acceso
   - Identificar alcance del incidente
   - Documentar hallazgos

3. RECUPERACIÓN:
   - Restaurar desde backup limpio
   - Aplicar parches de seguridad
   - Fortalecer medidas preventivas

4. SEGUIMIENTO:
   - Monitoreo intensivo
   - Revisión de procedimientos
   - Capacitación adicional
```

## 📚 **Recursos Adicionales**

- [Configuración del Sistema](/documentacion/admin/configuracion-del-sistema/)
- [Gestión de Usuarios](/documentacion/admin/gestion-de-usuarios/)
- [Mantenimiento](/documentacion/admin/mantenimiento/)

---

_🔒 **Importante**: La seguridad es responsabilidad de todos. Mantente informado sobre las mejores prácticas._
