# Sistema Unificado de Permisos - Ecodisseny

## 📋 Resumen Ejecutivo

El sistema Ecodisseny utiliza un **modelo unificado de permisos** basado en grupos de Django que controla el acceso tanto al sistema de documentación como al módulo CarregaHores. Esta arquitectura garantiza consistencia, mantenibilidad y seguridad en toda la aplicación.

## 🏗️ Arquitectura del Sistema

### Principio Fundamental
```
Usuario → Grupo Django → Permisos Unificados → Acceso a Módulos
```

**Un solo sistema de grupos controla:**
- 📚 Acceso a documentación por categorías
- ⏱️ Permisos en CarregaHores (presupuestos y recursos)
- 👤 Asignación y gestión de perfiles de usuario

## 🔐 Grupos y Niveles de Acceso

### 👑 Developer
**Usuarios:** `mulastone`
**Propósito:** Desarrollo y mantenimiento del sistema

**Permisos:**
- ✅ **Documentación:** Acceso completo (admin + dev + general + usuario)
- ✅ **CarregaHores:** Administrador completo (todos los presupuestos)
- ✅ **Django Admin:** Superusuario (acceso total)
- ✅ **Base de Datos:** Acceso directo via shell
- ✅ **Sistema:** Configuración y despliegue

### 🔧 Administradores
**Usuarios:** `gonzalo`, `admin_test`
**Propósito:** Gestión operativa y administrativa

**Permisos:**
- ✅ **Documentación:** admin + general + usuario
- ✅ **CarregaHores:** Administrador (todos los presupuestos y recursos)
- ✅ **Django Admin:** Staff (acceso a modelos asignados)
- ⚠️ **Limitaciones:** Sin acceso a documentación de desarrollo
- 📝 **Nota:** Pueden tener recurso asignado (ej: Gonzalo)

### 👥 Recursos
**Usuarios:** `sarah`, `pilar`, `santiago`, `roger`, `ana_garcia`, `user_test`
**Propósito:** Usuarios operativos del sistema

**Permisos:**
- ✅ **Documentación:** Solo documentación de usuario
- ✅ **CarregaHores:** Solo presupuestos donde están asignados
- ❌ **Django Admin:** Sin acceso (salvo casos específicos)
- 🔒 **Restricciones:** Filtrado automático por recurso asignado

## 🛠️ Implementación Técnica

### Helper Methods Centralizados

**Ubicación:** `maestros/models.py` - Clase `PerfilUsuario`

```python
@classmethod
def is_admin(cls, user):
    """Verifica si es admin (usado en documentación y CarregaHores)"""
    return (user.is_superuser or user.is_staff or 
            user.groups.filter(name='Administradores').exists())

@classmethod
def get_user_recurso(cls, user):
    """Obtiene el recurso asignado (para filtrado de presupuestos)"""
    try:
        return user.perfil.recurso
    except cls.DoesNotExist:
        return None
```

### Sistema de Documentación

**Ubicación:** `documentacion/models.py`

```python
class CategoriaDocumentacion(models.Model):
    grupos_permitidos = models.ManyToManyField(
        Group, 
        blank=True,
        help_text="Grupos que pueden acceder a esta categoría"
    )
```

**Categorías y Permisos:**
- `usuario` → Grupo: Recursos, Administradores
- `admin` → Grupo: Administradores, Developer  
- `dev` → Grupo: Developer
- `general` → Grupo: Administradores, Developer

### Sistema CarregaHores

**Ubicación:** `carregahores/views.py`

**Funciones de Control:**
```python
def can_access_pressupost(user, pressupost):
    """Control de acceso a presupuestos"""
    if is_admin(user):
        return True  # Admin ve todo
    
    recurso = get_user_recurso(user)
    if not recurso:
        return False
    
    # Solo presupuestos con líneas asignadas
    return pressupost.linies.filter(recurs=recurso).exists()
```

## 📊 Matriz de Permisos

| Funcionalidad | Developer | Administradores | Recursos |
|---------------|-----------|-----------------|----------|
| **Documentación Usuario** | ✅ | ✅ | ✅ |
| **Documentación Admin** | ✅ | ✅ | ❌ |
| **Documentación Dev** | ✅ | ❌ | ❌ |
| **Documentación General** | ✅ | ✅ | ❌ |
| **CarregaHores (todos)** | ✅ | ✅ | ❌ |
| **CarregaHores (asignados)** | ✅ | ✅ | ✅ |
| **Django Admin** | ✅ | ✅ | ❌ |
| **Gestión Usuarios** | ✅ | ✅ | ❌ |
| **Configuración Sistema** | ✅ | ❌ | ❌ |

## 🔧 Gestión de Usuarios

### Asignación de Grupos

```python
# Via Django Shell
from django.contrib.auth.models import User, Group

user = User.objects.get(username='nombre_usuario')
grupo = Group.objects.get(name='Recursos')  # o 'Administradores'
user.groups.add(grupo)
```

### Verificación de Permisos

```python
# Verificar grupo de usuario
user.groups.all()

# Verificar permisos específicos
from maestros.models import PerfilUsuario
PerfilUsuario.is_admin(user)
PerfilUsuario.get_user_recurso(user)
```

### Asignación de Recursos

```python
# Crear/actualizar perfil
from maestros.models import PerfilUsuario, Recurso

recurso = Recurso.objects.get(nom='Nombre Recurso')
perfil, created = PerfilUsuario.objects.get_or_create(user=user)
perfil.recurso = recurso
perfil.save()
```

## 🚨 Troubleshooting

### Usuario no ve documentación
1. **Verificar grupo asignado:** `user.groups.all()`
2. **Verificar categoría:** `CategoriaDocumentacion.objects.filter(grupos_permitidos__user=user)`
3. **Verificar permisos helper:** `PerfilUsuario.is_admin(user)`

### Usuario no ve presupuestos en CarregaHores
1. **Verificar si es admin:** `PerfilUsuario.is_admin(user)`
2. **Verificar recurso asignado:** `PerfilUsuario.get_user_recurso(user)`
3. **Verificar líneas presupuesto:** `pressupost.linies.filter(recurs=recurso)`

### Error de acceso a Django Admin
1. **Verificar is_staff:** `user.is_staff`
2. **Verificar grupo Administradores:** `user.groups.filter(name='Administradores')`
3. **Verificar permisos específicos del modelo**

## 📈 Ventajas del Sistema

### ✅ Consistencia
- Un solo lugar para gestionar permisos
- Mismos grupos para todos los módulos
- Helper methods centralizados

### ✅ Mantenibilidad  
- Cambios en grupos afectan todo el sistema
- Lógica de permisos centralizada
- Fácil debugging y auditoría

### ✅ Escalabilidad
- Nuevos módulos heredan automáticamente permisos
- Grupos reutilizables
- Arquitectura extensible

### ✅ Seguridad
- Control granular por módulo
- Filtrado automático de datos
- Separación clara de responsabilidades

## 🛣️ Roadmap Futuro

### Mejoras Planificadas
- [ ] Auditoría de accesos (logs de permisos)
- [ ] Permisos temporales (expiración automática)
- [ ] Grupos dinámicos por proyecto
- [ ] API de permisos para integraciones

### Consideraciones
- Mantener compatibilidad con grupos existentes
- Documentar cambios en permisos
- Probar exhaustivamente antes de deploy

---

## 📞 Contacto Técnico

**Desarrollador Principal:** mulastone  
**Administrador Sistema:** gonzalo  
**Documentación:** `/docs/admin/sistema-permisos.md`

**Última actualización:** Octubre 2025  
**Versión:** 1.0 - Sistema Unificado