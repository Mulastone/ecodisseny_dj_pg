# 🛠️ Documentación de Desarrollador

Documentación técnica especializada para el desarrollo, mantenimiento y extensión del sistema Ecodisseny.

## 📚 Índice de Documentación Técnica

### 🏗️ **Arquitectura y Aplicaciones**
- **[App Documentación - Developer Guide](app-documentacion.md)** ⭐
  - Arquitectura completa de la app de documentación
  - Modelos, views, permisos y sistema de archivos
  - Management commands y testing strategy
  - Performance y deployment considerations

### 🐳 **Infrastructure y Deployment**
- **[Docker - Explicación Detallada](docker-explicacion-detallada.md)**
  - Configuración de contenedores
  - Docker Compose y servicios
  - Volumes y networking

- **[Guía Completa VPS](guia-completa-vps.md)**
  - Deployment en servidor VPS
  - Configuración SSL y Nginx
  - Backup y mantenimiento

### 🔧 **Desarrollo y Herramientas**
- **APIs y Endpoints**
- **Testing y QA**
- **CI/CD Pipeline**
- **Monitorización y Logs**

## 🎯 Stack Tecnológico

### **Backend**
- **Django 5.2.x:** Framework principal
- **PostgreSQL:** Base de datos
- **Gunicorn:** Servidor WSGI en producción
- **python-decouple:** Configuración por variables de entorno

### **Frontend**
- **Jazzmin:** Admin interface
- **Bootstrap:** UI framework
- **JavaScript:** Interactividad
- **Markdown:** Documentación

### **Infrastructure**
- **Docker:** Containerización
- **Nginx:** Reverse proxy
- **Let's Encrypt:** SSL certificates
- **Linux VPS:** Hosting

## 🛠️ Apps del Sistema

### **📚 documentacion**
**Propósito:** Sistema de knowledge base con control de acceso  
**Modelos:** `CategoriaDocumentacion`, `DocumentoMarkdown`  
**Características:** Markdown processing, permisos por grupo, cache

### **⏱️ carregahores**
**Propósito:** Gestión de carga de horas por proyecto  
**Modelos:** `CarregaHores`, filtrado por recurso asignado  
**Características:** Bulk actions, permisos granulares

### **👥 maestros**
**Propósito:** Datos maestros del sistema  
**Modelos:** `Recurso`, `PerfilUsuario`, `TipusRecurso`  
**Características:** Helper methods para permisos

### **💰 pressupostos**
**Propósito:** Gestión de presupuestos y proyectos  
**Modelos:** `Pressupost`, `LiniaPressupost`  
**Características:** Cálculos automáticos, seguimiento

### **🏗️ projectes**
**Propósito:** Gestión de proyectos activos  
**Modelos:** `Projecte`, relaciones con presupuestos  
**Características:** Estados, seguimiento temporal

### **👤 accounts**
**Propósito:** Autenticación y perfiles  
**Características:** Login/logout, gestión usuarios

## 🔐 Sistema de Permisos Unificado

### **Grupos Base**
```python
# Grupos definidos en fixtures
GRUPOS = {
    'Developer': {
        'permisos': 'ALL',
        'documentacion': ['admin', 'dev', 'general', 'usuario'],
        'carregahores': 'admin_completo'
    },
    'Administradores': {
        'permisos': 'STAFF',
        'documentacion': ['admin', 'general', 'usuario'],
        'carregahores': 'admin_completo'
    },
    'Recursos': {
        'permisos': 'USER',
        'documentacion': ['usuario'],
        'carregahores': 'filtrado_por_recurso'
    }
}
```

### **Helper Methods Centralizados**
```python
# maestros/models.py - PerfilUsuario
@classmethod
def is_admin(cls, user):
    return (user.is_superuser or user.is_staff or 
            user.groups.filter(name='Administradores').exists())

@classmethod  
def get_user_recurso(cls, user):
    try:
        return user.perfil.recurso
    except cls.DoesNotExist:
        return None
```

## 🗄️ Base de Datos

### **Estructura Principal**
```sql
-- Usuarios y permisos
auth_user
auth_group
auth_user_groups

-- Maestros
maestros_recurso
maestros_perfilusuario  
maestros_tipusrecurso

-- Documentación
documentacion_categoriadocumentacion
documentacion_documentomarkdown

-- Carga horas
carregahores_carregahores

-- Presupuestos
pressupostos_pressupost
pressupostos_liniapressupost
```

### **Relaciones Clave**
- `User` → `PerfilUsuario` → `Recurso` (1:1:1)
- `User` → `Groups` → `CategoriaDocumentacion` (M:M:M)
- `Recurso` → `CarregaHores` (1:M) - filtrado automático
- `Pressupost` → `LiniaPressupost` → `Recurso` (1:M:1)

## 🚀 Development Workflow

### **Setup Local**
```bash
# Clonar repositorio
git clone https://github.com/Mulastone/ecodisseny_dj_pg.git
cd ecodisseny_dj_pg

# Levantar servicios
docker compose --env-file .env.dev up -d

# Verificar servicios
docker compose --env-file .env.dev ps

# Acceder shell Django
docker compose --env-file .env.dev exec web python manage.py shell
```

### **Comandos Útiles**
```bash
# Migrations
docker compose --env-file .env.dev exec web python manage.py makemigrations
docker compose --env-file .env.dev exec web python manage.py migrate

# Fixtures
docker compose --env-file .env.dev exec web python manage.py loaddata fixtures/

# Documentación
docker compose --env-file .env.dev exec web python manage.py cargar_documentacion

# Tests
docker compose --env-file .env.dev exec web python manage.py test

# Logs
docker compose --env-file .env.dev logs web --tail=50
```

### **Debugging**
```python
# Django shell - análisis de permisos
from django.contrib.auth.models import User
from maestros.models import PerfilUsuario

user = User.objects.get(username='sarah')
print(f"Admin: {PerfilUsuario.is_admin(user)}")
print(f"Recurso: {PerfilUsuario.get_user_recurso(user)}")
print(f"Grupos: {[g.name for g in user.groups.all()]}")
```

## 📊 Métricas y Monitorización

### **Logs Importantes**
- **Django:** `/var/log/django/`
- **Nginx:** `/var/log/nginx/`
- **PostgreSQL:** `/var/log/postgresql/`
- **Docker:** `docker-compose logs [service]`

### **Health Checks**
- **Web:** `GET /admin/` (status 200)
- **DB:** Connection test via shell
- **Cache:** Redis ping
- **Storage:** Filesystem access

## 🧪 Testing Strategy

### **Niveles de Testing**
```bash
# Unit tests por app
python manage.py test documentacion
python manage.py test carregahores  
python manage.py test maestros

# Integration tests
python manage.py test --pattern="*integration*"

# Performance tests
python manage.py test --pattern="*performance*"
```

### **Coverage**
```bash
# Instalar coverage
pip install coverage

# Ejecutar con coverage
coverage run --source='.' manage.py test
coverage report -m
coverage html
```

## 🔧 Configuración Avanzada

### **Environment Variables**
```bash
# .env file
DATABASE_URL=postgresql://user:pass@db:5432/ecodisseny
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

### **Django Settings**
```python
# settings.py - Configuraciones clave
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}

# Jazzmin customization
JAZZMIN_SETTINGS = {
    'site_title': 'Ecodisseny Admin',
    'custom_css': 'css/admin_custom.css',
}
```

## 📈 Roadmap Técnico

### **Q1 2025**
- [ ] API REST completa
- [ ] Swagger/OpenAPI documentation
- [ ] Advanced caching strategy
- [ ] Performance optimization

### **Q2 2025**
- [ ] Microservices architecture
- [ ] Kubernetes deployment
- [ ] Advanced monitoring (Prometheus/Grafana)
- [ ] CI/CD with GitHub Actions

### **Q3 2025**
- [ ] Real-time features (WebSockets)
- [ ] Mobile app backend
- [ ] Advanced analytics
- [ ] Machine learning integration

---

## 📞 Development Support

**Lead Developer:** mulastone  
**Repository:** `https://github.com/Mulastone/ecodisseny_dj_pg`  
**Branch:** `docker` (main development)  
**Documentation:** `/documentacion/dev/`  

**Development Environment:**
- **OS:** Linux (Ubuntu/Debian)
- **Docker:** Latest stable
- **Python:** 3.12+
- **Node.js:** 18+ (for frontend tools)

**Contacts:**
- **Technical Issues:** Create GitHub issue
- **Architecture Decisions:** mulastone
- **Code Review:** Pull request required

**Última actualización:** Octubre 2025  
**Versión:** 1.0 - Developer Documentation
