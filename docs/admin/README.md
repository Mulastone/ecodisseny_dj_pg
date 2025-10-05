# 🔧 Documentación de Administrador

Documentación técnica y operativa para administradores del sistema Ecodisseny.

## 📚 Índice de Documentación

### 🔐 **Sistema de Permisos y Seguridad**
- **[Sistema Unificado de Permisos](sistema-permisos/)** ⭐
  - Arquitectura completa del sistema de permisos
  - Grupos de usuarios y niveles de acceso
  - Helper methods y implementación técnica
  - Troubleshooting y gestión de usuarios

### ⚙️ **Configuración del Sistema**
- **[Configuración Inicial](configuracion/)**
  - Setup inicial del sistema
  - Datos maestros (recursos, ubicaciones, tareas)
  - Usuarios y permisos básicos
  - Configuración de seguridad

### 👥 **Gestión de Usuarios**
- **Creación y asignación de usuarios**
- **Gestión de grupos y permisos**
- **Configuración de recursos y perfiles**

### 📊 **Módulos del Sistema**
- **CarregaHores:** Gestión de carga de horas
- **Presupuestos:** Administración de proyectos
- **Maestros:** Datos base del sistema
- **Documentación:** Sistema de knowledge base

## 🎯 Accesos Rápidos

### 🌐 **URLs Importantes**
- **Panel Admin:** `/admin/`
- **CarregaHores:** `/carregahores/`
- **Documentación:** `/documentacion/`
- **API Admin:** `/admin/login/`

### 👤 **Usuarios de Referencia**
- **Developer:** `mulastone` (acceso completo)
- **Admin:** `gonzalo` (gestión operativa)
- **Recursos:** `sarah`, `pilar`, etc. (usuarios finales)

### 🔐 **Grupos del Sistema**
- **Developer:** Desarrollo y mantenimiento
- **Administradores:** Gestión operativa
- **Recursos:** Usuarios finales del sistema

## 🚨 Enlaces de Emergencia

### **Troubleshooting**
- **[Guía de Resolución de Problemas](/docs/troubleshooting.md)**
- **Logs del sistema:** `docker-compose logs web`
- **Shell de Django:** `docker-compose exec web python manage.py shell`

### **Contactos Técnicos**
- **Desarrollador Principal:** mulastone
- **Administrador Sistema:** gonzalo
- **Soporte:** Ver documentación específica

---

## 📈 Próximas Actualizaciones

- [ ] Guía de backup y recuperación
- [ ] Configuración de notificaciones
- [ ] Integración con sistemas externos
- [ ] Métricas y monitorización

**Última actualización:** Octubre 2025  
**Versión:** 1.0 - Sistema Unificado