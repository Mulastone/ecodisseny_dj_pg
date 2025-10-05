# 🛠️ Documentación App - Developer Guide

## 📋 Resumen Técnico

La aplicación `documentacion` es un sistema de **knowledge base dinámico** que gestiona documentación categorizada con control de acceso basado en grupos. Diseñada para servir diferentes tipos de usuarios (recursos, administradores, desarrolladores) con contenido específico y permisos granulares.

## 🏗️ Arquitectura de la Aplicación

### **Estructura del Módulo**
```
documentacion/
├── __init__.py
├── admin.py                 # Django Admin configuration
├── apps.py                  # App configuration
├── models.py               # Core models (CategoriaDocumentacion, DocumentoMarkdown)
├── views.py                # Views and business logic
├── urls.py                 # URL routing
├── tests.py                # Unit tests
├── management/             # Management commands
│   └── commands/
│       └── cargar_documentacion.py
└── migrations/             # Database migrations
```

### **Dependencias Principales**
- **Django 4.x:** Framework base
- **Markdown:** Procesamiento de archivos .md
- **Django Groups:** Sistema de permisos
- **Bootstrap/Jazzmin:** UI components

## 🗄️ Modelos de Datos

### **CategoriaDocumentacion**
```python
class CategoriaDocumentacion(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_CATEGORIA)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, default="📚")
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    
    # Control de acceso
    grupos_permitidos = models.ManyToManyField(Group, blank=True)
```

**Propósito:** Define categorías de documentación con control granular de acceso por grupos.

**Tipos disponibles:**
- `usuario` → 👤 Documentación para usuarios finales
- `admin` → 🔧 Documentación administrativa  
- `dev` → 🛠️ Documentación técnica
- `general` → 📚 Documentación general

### **DocumentoMarkdown**
```python
class DocumentoMarkdown(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField()
    categoria = models.ForeignKey(CategoriaDocumentacion, on_delete=models.CASCADE)
    
    # Archivo físico
    archivo_markdown = models.CharField(max_length=500)  # Path al .md
    resumen = models.TextField(blank=True)
    
    # Metadatos
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Estado
    publicado = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    palabras_clave = models.CharField(max_length=500, blank=True)
```

**Propósito:** Representa documentos individuales vinculados a archivos físicos .md con metadatos completos.

## 🔐 Sistema de Permisos

### **Flujo de Autorización**
```python
def categoria_accesible_para_usuario(categoria, user):
    """
    Verifica si un usuario puede acceder a una categoría
    """
    if not categoria.grupos_permitidos.exists():
        return True  # Sin restricciones
    
    return categoria.grupos_permitidos.filter(
        id__in=user.groups.values_list('id', flat=True)
    ).exists()
```

### **Implementación en Views**
```python
def lista_documentacion(request):
    categorias_accesibles = CategoriaDocumentacion.objects.filter(
        activa=True
    )
    
    if not request.user.is_superuser:
        # Filtrar por grupos del usuario
        user_groups = request.user.groups.values_list('id', flat=True)
        categorias_accesibles = categorias_accesibles.filter(
            Q(grupos_permitidos__isnull=True) |
            Q(grupos_permitidos__in=user_groups)
        ).distinct()
```

### **Matriz de Acceso**
| Grupo | usuario | admin | dev | general |
|-------|---------|-------|-----|---------|
| **Recursos** | ✅ | ❌ | ❌ | ❌ |
| **Administradores** | ✅ | ✅ | ❌ | ✅ |
| **Developer** | ✅ | ✅ | ✅ | ✅ |

## 📁 Gestión de Archivos

### **Estructura de Archivos**
```
docs/
├── usuario/               # Documentación usuario final
│   ├── inicio-rapido.md
│   ├── carga-horas.md
│   └── mi-perfil.md
├── admin/                 # Documentación administrativa
│   ├── README.md
│   ├── sistema-permisos.md
│   ├── configuracion.md
│   └── mantenimiento.md
├── dev/                   # Documentación desarrollo
│   ├── README.md
│   ├── app-documentacion.md
│   └── deployment.md
└── general/               # Documentación general
    ├── README.md
    └── empresa.md
```

### **Procesamiento de Markdown**
```python
def obtener_contenido_markdown(self):
    """
    Lee y procesa el archivo markdown
    """
    try:
        file_path = os.path.join(settings.BASE_DIR, self.archivo_markdown)
        with open(file_path, 'r', encoding='utf-8') as file:
            contenido_raw = file.read()
        
        # Procesar markdown a HTML
        html_content = markdown.markdown(
            contenido_raw, 
            extensions=['codehilite', 'toc', 'tables']
        )
        return html_content
        
    except FileNotFoundError:
        return "<p>⚠️ Archivo no encontrado</p>"
```

## 🌐 URLs y Routing

### **Configuración de URLs**
```python
# documentacion/urls.py
app_name = 'documentacion'

urlpatterns = [
    path('', views.lista_documentacion, name='lista'),
    path('<slug:categoria_slug>/', views.categoria_documentacion, name='categoria'),
    path('<slug:categoria_slug>/<slug:documento_slug>/', views.documento_detalle, name='documento'),
]

# ecodisseny/urls.py
urlpatterns = [
    path('documentacion/', include('documentacion.urls')),
]
```

### **Patrones de URL**
- `/documentacion/` → Lista de categorías accesibles
- `/documentacion/admin/` → Documentos administrativos
- `/documentacion/admin/sistema-permisos/` → Documento específico

## 🎨 Templates y UI

### **Template Hierarchy**
```
templates/documentacion/
├── base_documentacion.html        # Layout base
├── lista_documentacion.html       # Índice categorías
├── categoria_documentacion.html   # Lista documentos por categoría
└── documento_detalle.html         # Visualización documento
```

### **Context Processors**
```python
def documentacion_context(request):
    """
    Añade contexto global para navegación
    """
    if request.user.is_authenticated:
        categorias_nav = CategoriaDocumentacion.objects.filter(
            activa=True,
            grupos_permitidos__in=request.user.groups.all()
        ).distinct()
    else:
        categorias_nav = CategoriaDocumentacion.objects.filter(
            activa=True,
            grupos_permitidos__isnull=True
        )
    
    return {'categorias_nav': categorias_nav}
```

## ⚙️ Management Commands

### **cargar_documentacion.py**
```python
class Command(BaseCommand):
    """
    Comando para sincronizar archivos .md con base de datos
    """
    
    def handle(self, *args, **options):
        self.cargar_categorias()
        self.cargar_documentos()
        self.validar_archivos()
```

**Uso:**
```bash
python manage.py cargar_documentacion
python manage.py cargar_documentacion --categoria=admin
python manage.py cargar_documentacion --validar-solo
```

## 🔍 Funcionalidades Avanzadas

### **Búsqueda de Documentos**
```python
def buscar_documentos(query, user):
    """
    Búsqueda inteligente con permisos
    """
    documentos = DocumentoMarkdown.objects.filter(
        Q(titulo__icontains=query) |
        Q(resumen__icontains=query) |
        Q(palabras_clave__icontains=query),
        publicado=True
    )
    
    # Filtrar por permisos de categoría
    categorias_accesibles = obtener_categorias_accesibles(user)
    documentos = documentos.filter(categoria__in=categorias_accesibles)
    
    return documentos
```

### **Documentos Destacados**
```python
def obtener_documentos_destacados(user):
    """
    Documentos marcados como destacados para el usuario
    """
    categorias = obtener_categorias_accesibles(user)
    return DocumentoMarkdown.objects.filter(
        categoria__in=categorias,
        destacado=True,
        publicado=True
    ).order_by('-fecha_actualizacion')
```

### **Navegación Contextual**
```python
def obtener_navegacion_documento(documento):
    """
    Genera navegación anterior/siguiente dentro de la categoría
    """
    categoria = documento.categoria
    documentos = categoria.documentos.filter(publicado=True).order_by('orden', 'titulo')
    
    actual_index = list(documentos).index(documento)
    
    anterior = documentos[actual_index - 1] if actual_index > 0 else None
    siguiente = documentos[actual_index + 1] if actual_index < len(documentos) - 1 else None
    
    return {'anterior': anterior, 'siguiente': siguiente}
```

## 🧪 Testing Strategy

### **Tests de Modelos**
```python
class DocumentacionModelsTest(TestCase):
    def test_categoria_permisos(self):
        """Test acceso por grupos"""
        categoria = CategoriaDocumentacion.objects.create(
            nombre="Test", slug="test", tipo="admin"
        )
        admin_group = Group.objects.create(name="Administradores")
        categoria.grupos_permitidos.add(admin_group)
        
        # Usuario con grupo
        user_admin = User.objects.create_user("admin", groups=[admin_group])
        self.assertTrue(categoria_accesible_para_usuario(categoria, user_admin))
        
        # Usuario sin grupo
        user_normal = User.objects.create_user("normal")
        self.assertFalse(categoria_accesible_para_usuario(categoria, user_normal))
```

### **Tests de Views**
```python
class DocumentacionViewsTest(TestCase):
    def test_lista_documentacion_permisos(self):
        """Test filtrado por permisos en vista lista"""
        response = self.client.get('/documentacion/')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que solo aparecen categorías permitidas
        categorias_response = response.context['categorias']
        for categoria in categorias_response:
            self.assertTrue(categoria_accesible_para_usuario(categoria, self.user))
```

## 🚀 Deployment y Performance

### **Optimizaciones**
- **Prefetch relacionado:** `select_related('categoria', 'autor')`
- **Cache de markdown:** Redis para contenido procesado
- **Lazy loading:** Carga diferida de archivos grandes
- **CDN:** Archivos estáticos via CDN

### **Monitorización**
```python
import logging

logger = logging.getLogger('documentacion')

def documento_detalle(request, categoria_slug, documento_slug):
    logger.info(f"Acceso documento: {documento_slug} por {request.user.username}")
    # ... resto de la vista
```

## 🔧 Configuración

### **Settings Variables**
```python
# settings.py
DOCUMENTACION_CONFIG = {
    'MARKDOWN_EXTENSIONS': ['codehilite', 'toc', 'tables', 'fenced_code'],
    'CACHE_TIMEOUT': 3600,  # 1 hora
    'ARCHIVOS_BASE_PATH': os.path.join(BASE_DIR, 'docs'),
    'PERMITIR_ACCESO_ANONIMO': False,
}
```

### **Señales Django**
```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=DocumentoMarkdown)
def invalidar_cache_documento(sender, instance, **kwargs):
    """Invalida cache cuando se actualiza un documento"""
    cache_key = f"documento_{instance.id}"
    cache.delete(cache_key)
```

## 📈 Roadmap Técnico

### **Próximas Funcionalidades**
- [ ] **API REST:** Endpoints para integración externa
- [ ] **Versioning:** Control de versiones de documentos
- [ ] **Comentarios:** Sistema de feedback por documento
- [ ] **Analytics:** Métricas de uso y acceso
- [ ] **Export:** PDF/Word generation
- [ ] **Search:** Full-text search con Elasticsearch

### **Mejoras Técnicas**
- [ ] **Async Views:** Para mejor performance
- [ ] **WebSockets:** Updates en tiempo real
- [ ] **GraphQL:** API más eficiente
- [ ] **Docker:** Containerización completa
- [ ] **CI/CD:** Automated testing y deployment

---

## 📞 Development Support

**Arquitecto Principal:** mulastone  
**Repositorio:** `ecodisseny_dj_pg`  
**Rama Desarrollo:** `docker`  
**Documentación API:** `/admin/doc/`

**Comandos Útiles:**
```bash
# Desarrollo
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py cargar_documentacion

# Testing
docker-compose exec web python manage.py test documentacion

# Logs
docker-compose logs web --tail=50
```

**Última actualización:** Octubre 2025  
**Versión:** 1.0 - Knowledge Base System