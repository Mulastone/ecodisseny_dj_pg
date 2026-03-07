# 👥 Gestión de Usuarios y Permisos

Esta guía detalla cómo administrar usuarios, roles y permisos en Ecodisseny para mantener un sistema seguro y eficiente.

## 🎯 Conceptos Clave

### **👤 Usuario vs Recurso vs Perfil**

| Concepto       | Descripción                   | Ejemplo                               |
| -------------- | ----------------------------- | ------------------------------------- |
| **👤 Usuario** | Cuenta de acceso al sistema   | `maria.garcia` (login)                |
| **🏗️ Recurso** | Persona física que trabaja    | "María García López" (datos maestros) |
| **🔗 Perfil**  | Vinculación Usuario ↔ Recurso | maria.garcia → María García López     |

### **🔐 Niveles de Acceso**

```
🔴 Superusuario (mulastone)
├── 🟠 Administradores (Staff)
├── 🟡 Jefes de Proyecto
├── 🟢 Usuarios Normales
└── 🔵 Solo Lectura
```

## 👥 Gestión de Usuarios

## SOP: Alta de Recurso Interno/Colaborador (flujo recomendado)

Este es el flujo operativo recomendado para evitar descuadres entre `Usuario`, `Recurso` y `Perfil`.

### Regla de negocio

- `Intern` y `Colaborador`: necesitan usuario de login.
- `Extern`: no necesita usuario de login (solo recurso maestro).

`Necessita Usuari` se calcula automaticamente por tipo de recurso.

### Flujo optimo (1 paso con comando)

No hace falta crear usuario previamente en Admin si usas este comando.
El comando crea/actualiza: tipo de recurso, recurso, usuario y perfil enlazado.

```bash
cd /opt/ecodisseny/ecodisseny_dj_pg
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web \
python manage.py crear_recurso_usuari \
  --username roger \
  --first_name Roger \
  --email roger@ecodisseny.com \
  --password 'Cambiar123!' \
  --recurso_name Roger \
  --tipo_recurso Colaborador \
  --preu_hora 19.60
```

Opcional admin:

```bash
# agrega acceso al admin si corresponde
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web \
python manage.py crear_recurso_usuari \
  --username gonzalo \
  --first_name Gonzalo \
  --email gonzalo@ecodisseny.com \
  --password 'Cambiar123!' \
  --recurso_name Gonzalo \
  --tipo_recurso Intern \
  --is_staff
```

### Flujo para recurso Extern

1. Crear solo `Recurso` en Admin (`Tipus recurso = Extern`).
2. No crear usuario salvo requerimiento excepcional.

### Validacion post-alta (obligatoria)

1. En Admin > Usuarios, el usuario existe y esta activo.
2. En Admin > PerfilUsuario, el usuario apunta al recurso correcto.
3. Login con el usuario y prueba de acceso a carga de horas.

### Flujo alternativo manual (si no usas comando)

1. Crear recurso.
2. Crear usuario.
3. Asignar perfil (`Usuario -> Recurso`) en Admin.
4. Validar acceso.

Evita depender de autoasignacion por coincidencia de nombres como flujo principal.

### Flujo optimo sin terminal (Admin no tecnico)

Tambien disponible en una pantalla unica dentro del Admin:

1. `Moduls Maestros > Recursos`
2. Boton: **Alta completa intern/colaborador**
3. Completar formulario y guardar

Este formulario crea/actualitza en una sola accion:
- Recurso
- Usuario
- Perfil (enlace Usuario -> Recurso)

Acces rapid adicional:
- desde `Moduls Maestros > Tipus de Recurs > (detalle del tipo)` puedes usar
  **Alta completa amb aquest tipus** para abrir el mismo formulario con el tipo preseleccionado.

### **➕ Crear Nuevo Usuario**

#### **1. Acceso al Panel Admin**

1. **Admin Panel** → **Autenticación y autorización** → **Usuarios**
2. **"Añadir Usuario"**

#### **2. Datos Básicos Obligatorios**

| Campo        | Descripción             | Ejemplo                | Reglas                   |
| ------------ | ----------------------- | ---------------------- | ------------------------ |
| **Username** | Nombre de usuario único | `maria.garcia`         | Sin espacios, minúsculas |
| **Password** | Contraseña temporal     | `EcoTemp2025!`         | Mín 8 caracteres         |
| **Email**    | Correo electrónico      | `maria@ecodisseny.com` | Único en el sistema      |

#### **3. Información Personal**

| Campo         | Obligatorio | Ejemplo              |
| ------------- | ----------- | -------------------- |
| **Nombre**    | ✅ Sí       | María                |
| **Apellidos** | ✅ Sí       | García López         |
| **Email**     | ✅ Sí       | maria@ecodisseny.com |

#### **4. Configuración de Permisos**

**Marcar las opciones apropiadas**:

| Opción           | Descripción           | ¿Cuándo usar?                     |
| ---------------- | --------------------- | --------------------------------- |
| **Activo**       | Usuario puede acceder | ✅ Siempre para usuarios normales |
| **Staff**        | Acceso al panel admin | ✅ Solo administradores           |
| **Superusuario** | Acceso total          | ⚠️ Solo casos especiales          |

### **🔗 Vincular Usuario con Recurso**

#### **Crear Perfil de Usuario**

1. **Admin Panel** → **Carga hores** → **Perfiles de usuario**
2. **"Añadir Perfil de usuario"**
3. **Configurar vinculación**:
   - **Usuario**: Seleccionar de la lista
   - **Recurso**: Persona física correspondiente
   - **Fecha alta**: Cuándo empieza a trabajar

#### **💡 Ejemplo Completo**

```
👤 Usuario del Sistema:
   Username: maria.garcia
   Email: maria@ecodisseny.com
   Nombre: María García López

🏗️ Recurso (Datos Maestros):
   Código: MAR001
   Nombre: María García López
   Tipo: Arquitecto
   Especialidad: Rehabilitación

🔗 Perfil (Vinculación):
   Usuario: maria.garcia ↔ Recurso: MAR001
   Fecha Alta: 15/08/2025
```

## 🔐 Sistema de Permisos

### **📋 Grupos de Usuarios**

#### **🟠 Grupo: Administradores**

**Características**:

- ✅ **Acceso total** al panel admin
- ✅ **Gestión** de usuarios y permisos
- ✅ **Configuración** del sistema
- ✅ **Todas** las funciones de la aplicación

**Permisos específicos**:

```
👥 Usuarios: Crear, editar, eliminar, cambiar permisos
🏗️ Proyectos: CRUD completo, cambiar estados
💰 Presupuestos: CRUD completo, aprobar/rechazar
⏱️ Horas: Ver todas, editar todas, generar reportes
📊 Reportes: Acceso a todos los reportes
🔧 Maestros: Configurar recursos, ubicaciones, tareas
```

#### **🟡 Grupo: Jefes de Proyecto**

**Características**:

- ✅ **Gestión completa** de sus proyectos
- ✅ **Supervisión** del equipo asignado
- ✅ **Reportes** de sus proyectos
- ❌ **No acceso** al panel admin

**Permisos específicos**:

```
🏗️ Proyectos: Crear, editar (propios), ver (todos)
💰 Presupuestos: CRUD en proyectos asignados
⏱️ Horas: Ver/editar equipo, registrar propias
📊 Reportes: Proyectos propios y equipo
👥 Equipo: Ver información básica del equipo
```

#### **🟢 Grupo: Usuarios Normales**

**Características**:

- ✅ **Trabajar** en proyectos asignados
- ✅ **Registrar** horas trabajadas
- ✅ **Ver** información de sus proyectos
- ❌ **No crear** proyectos (solo asignados)

**Permisos específicos**:

```
🏗️ Proyectos: Ver asignados, editar datos básicos
💰 Presupuestos: Ver relacionados con sus proyectos
⏱️ Horas: Registrar propias, editar propias
📊 Reportes: Solo de su trabajo personal
👤 Perfil: Editar datos personales
```

#### **🔵 Grupo: Solo Lectura**

**Características**:

- ✅ **Consultar** información
- ✅ **Ver** reportes básicos
- ❌ **No modificar** nada
- ❌ **No registrar** horas

**Permisos específicos**:

```
🏗️ Proyectos: Solo lectura
💰 Presupuestos: Solo lectura
⏱️ Horas: Solo lectura
📊 Reportes: Básicos únicamente
```

### **⚙️ Configurar Grupos**

#### **1. Crear Grupo**

1. **Admin Panel** → **Autenticación** → **Grupos**
2. **"Añadir Grupo"**
3. **Nombre**: "Jefes de Proyecto"

#### **2. Asignar Permisos**

**Seleccionar permisos específicos**:

| Aplicación       | Modelo        | Permisos a Asignar                    |
| ---------------- | ------------- | ------------------------------------- |
| **Projectes**    | Projecte      | ✅ add, ✅ change, ✅ view, ⚠️ delete |
| **Pressupostos** | Pressupost    | ✅ add, ✅ change, ✅ view, ❌ delete |
| **Carregahores** | RegistreHores | ✅ add, ✅ change, ✅ view            |
| **Maestros**     | Recurso       | ✅ view                               |

#### **3. Asignar Usuarios al Grupo**

1. **Editar Usuario** → **Grupos**
2. **Mover grupo** de "Disponibles" a "Elegidos"
3. **Guardar**

## 🎯 Casos de Uso Específicos

### **👷 Caso 1: Nuevo Operario**

```
Situación: Juan Pérez se incorpora como operario

1. 🏗️ Crear Recurso en Maestros:
   - Código: JUA003
   - Nombre: Juan Pérez Martín
   - Tipo: Operario Especializado

2. 👤 Crear Usuario:
   - Username: juan.perez
   - Email: juan@ecodisseny.com
   - Grupo: Usuarios Normales

3. 🔗 Crear Perfil:
   - Usuario: juan.perez ↔ Recurso: JUA003

4. ✅ Resultado:
   - Puede registrar horas
   - Ve proyectos asignados
   - No puede crear proyectos
```

### **🏗️ Caso 2: Promoción a Jefe de Proyecto**

```
Situación: María pasa de operario a jefe de proyecto

1. 👤 Editar Usuario maria.garcia:
   - Quitar de: "Usuarios Normales"
   - Añadir a: "Jefes de Proyecto"

2. 🏗️ Actualizar Recurso:
   - Tipo: Jefe de Proyecto
   - Especialidad: Gestión de Obras

3. ✅ Resultado:
   - Puede crear proyectos
   - Supervisa equipos
   - Acceso a reportes avanzados
```

### **👨‍💼 Caso 3: Administrador Temporal**

```
Situación: Pedro necesita acceso admin por 1 mes

1. 👤 Editar Usuario pedro.admin:
   - Marcar: ✅ Staff status
   - Añadir a: "Administradores"

2. 📅 Programar recordatorio:
   - Revisar en 30 días
   - Quitar permisos admin

3. ⚠️ Documentar:
   - Fecha inicio: 15/08/2025
   - Fecha fin: 15/09/2025
   - Motivo: Vacaciones administrador principal
```

## 🔒 Configuración de Seguridad

### **🛡️ Políticas de Contraseñas**

#### **Configuración Actual**

```python
# Django settings (ya configurado)
AUTH_PASSWORD_VALIDATORS = [
    'UserAttributeSimilarityValidator',  # No similar a datos usuario
    'MinimumLengthValidator',            # Mínimo 8 caracteres
    'CommonPasswordValidator',           # No contraseñas comunes
    'NumericPasswordValidator',          # No solo números
]
```

#### **Forzar Cambio de Contraseña**

```python
# Para usuarios nuevos
user.set_password('TemporalPass2025!')
user.save()

# Marcar para cambio obligatorio (personalizado)
profile.requires_password_change = True
profile.save()
```

### **🔄 Rotación de Credenciales**

#### **Política Recomendada**

- **Administradores**: Cambio cada 90 días
- **Usuarios normales**: Cambio cada 180 días
- **Cuentas de servicio**: Cambio cada 365 días

#### **Implementar Recordatorios**

```python
# Script de recordatorio (ejecutar en cron)
from datetime import datetime, timedelta
from django.contrib.auth.models import User

# Usuarios con contraseñas viejas (90 días)
old_passwords = User.objects.filter(
    date_joined__lt=datetime.now() - timedelta(days=90),
    last_login__lt=datetime.now() - timedelta(days=90)
)

for user in old_passwords:
    # Enviar email de recordatorio
    send_password_reminder(user)
```

## 📊 Monitoreo de Usuarios

### **📈 Métricas Importantes**

#### **Actividad de Usuarios**

```sql
-- Usuarios activos en los últimos 30 días
SELECT COUNT(*) FROM auth_user
WHERE last_login >= NOW() - INTERVAL '30 days';

-- Usuarios inactivos (más de 90 días)
SELECT username, last_login FROM auth_user
WHERE last_login < NOW() - INTERVAL '90 days'
OR last_login IS NULL;
```

#### **Dashboard de Administrador**

- 👥 **Usuarios totales**: 45
- 🟢 **Activos (30 días)**: 38
- 🟡 **Inactivos (30-90 días)**: 5
- 🔴 **Nunca accedieron**: 2

### **🚨 Alertas de Seguridad**

#### **Configurar Alertas**

- 🔒 **Intentos de login fallidos** (>5 en 1 hora)
- 👤 **Nuevos usuarios** creados
- 🔧 **Cambios de permisos** importantes
- 🕐 **Accesos fuera de horario** laboral

## 🛠️ Herramientas de Administración

### **📝 Scripts Útiles**

#### **1. Crear Usuario Completo**

```python
# create_user.py
from django.contrib.auth.models import User, Group
from maestros.models import Recurso
from carregahores.models import PerfilUsuario

def create_complete_user(username, email, full_name, resource_type, group_name):
    # 1. Crear usuario
    user = User.objects.create_user(
        username=username,
        email=email,
        password='TemporalPass2025!',
        first_name=full_name.split()[0],
        last_name=' '.join(full_name.split()[1:])
    )

    # 2. Asignar grupo
    group = Group.objects.get(name=group_name)
    user.groups.add(group)

    # 3. Crear recurso
    resource = Recurso.objects.create(
        nom=full_name,
        tipus_recurso=resource_type,
        codi=username.upper()[:6]
    )

    # 4. Crear perfil
    profile = PerfilUsuario.objects.create(
        user=user,
        recurso=resource
    )

    return user, resource, profile

# Uso:
create_complete_user(
    'ana.lopez',
    'ana@ecodisseny.com',
    'Ana López García',
    'Arquitecto',
    'Jefes de Proyecto'
)
```

#### **2. Informe de Usuarios**

```python
# user_report.py
from django.contrib.auth.models import User
from datetime import datetime, timedelta

def generate_user_report():
    total_users = User.objects.count()
    active_users = User.objects.filter(
        last_login__gte=datetime.now() - timedelta(days=30)
    ).count()

    inactive_users = User.objects.filter(
        last_login__lt=datetime.now() - timedelta(days=90)
    )

    print(f"=== INFORME DE USUARIOS ===")
    print(f"Total usuarios: {total_users}")
    print(f"Activos (30 días): {active_users}")
    print(f"Inactivos (90+ días): {inactive_users.count()}")
    print()
    print("Usuarios inactivos:")
    for user in inactive_users:
        last_login = user.last_login or "Nunca"
        print(f"  - {user.username}: {last_login}")
```

### **🔧 Comandos Django Útiles**

```bash
# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Cambiar contraseña de usuario
docker-compose exec web python manage.py changepassword username

# Listar usuarios activos
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
for u in User.objects.filter(is_active=True):
    print(f'{u.username}: {u.email}')
"

# Desactivar usuario
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='usuario_a_desactivar')
user.is_active = False
user.save()
print('Usuario desactivado')
"
```

## 🆘 Resolución de Problemas

### **❓ "Usuario no puede acceder"**

**Diagnóstico paso a paso**:

```python
# 1. Verificar usuario existe
User.objects.filter(username='problema_user').exists()

# 2. Verificar está activo
user = User.objects.get(username='problema_user')
print(f"Activo: {user.is_active}")
print(f"Último acceso: {user.last_login}")

# 3. Verificar contraseña
user.check_password('contraseña_probada')

# 4. Verificar permisos
print(f"Grupos: {user.groups.all()}")
print(f"Permisos: {user.user_permissions.all()}")
```

### **❓ "Usuario ve datos de otros"**

**Verificar permisos**:

```python
# Verificar configuración de grupos
user = User.objects.get(username='usuario_problema')
for group in user.groups.all():
    print(f"Grupo: {group.name}")
    for perm in group.permissions.all():
        print(f"  - {perm.codename}")
```

### **❓ "No se puede crear perfil"**

**Causas comunes**:

- ✅ **Recurso ya vinculado** → Un recurso solo puede tener un perfil
- ✅ **Usuario ya tiene perfil** → Un usuario solo puede tener un perfil
- ✅ **Recurso inexistente** → Crear el recurso primero

## 📞 Soporte

### **🆘 Contacto Urgente**

- **Email**: usuarios@ecodisseny.com
- **Interno**: Extensión 101
- **WhatsApp**: +376 XXX XXX

### **📚 Documentación Relacionada**

- [🔐 Seguridad Avanzada](seguridad.md)
- [🏗️ Datos Maestros](gestion-de-maestros.md)
- [📊 Mantenimiento](mantenimiento.md)

---

_🎯 **Siguiente paso**: Configurar [datos maestros](gestion-de-maestros.md) del sistema._
