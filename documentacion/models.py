from django.db import models
from django.contrib.auth.models import User, Group
from django.urls import reverse
import markdown
import os


class CategoriaDocumentacion(models.Model):
    """Categorías de documentación según tipo de usuario"""
    
    TIPOS_CATEGORIA = [
        ('usuario', '👤 Usuario'),
        ('admin', '🔧 Administrador'), 
        ('dev', '🛠️ Desarrollador'),
        ('general', '📚 General'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True, verbose_name="URL amigable")
    tipo = models.CharField(max_length=20, choices=TIPOS_CATEGORIA, verbose_name="Tipo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    icono = models.CharField(max_length=50, default="📚", verbose_name="Icono")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    
    # Permisos de acceso
    grupos_permitidos = models.ManyToManyField(
        Group, 
        blank=True, 
        verbose_name="Grupos con acceso",
        help_text="Si no se especifica, todos los usuarios autenticados tienen acceso"
    )
    
    class Meta:
        verbose_name = "Categoría de Documentación"
        verbose_name_plural = "Categorías de Documentación"
        ordering = ['tipo', 'orden', 'nombre']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"


class DocumentoMarkdown(models.Model):
    """Documento de documentación en formato Markdown"""
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(verbose_name="URL amigable")
    categoria = models.ForeignKey(
        CategoriaDocumentacion, 
        on_delete=models.CASCADE, 
        verbose_name="Categoría"
    )
    
    # Contenido
    archivo_markdown = models.CharField(
        max_length=500, 
        verbose_name="Ruta del archivo .md",
        help_text="Ejemplo: docs/usuario/inicio-rapido.md"
    )
    resumen = models.TextField(blank=True, verbose_name="Resumen")
    
    # Metadatos
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    autor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Autor"
    )
    
    # Configuración
    publicado = models.BooleanField(default=True, verbose_name="Publicado")
    destacado = models.BooleanField(default=False, verbose_name="Destacado")
    
    # SEO y búsqueda
    palabras_clave = models.CharField(
        max_length=500, 
        blank=True, 
        verbose_name="Palabras clave",
        help_text="Separadas por comas"
    )
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['categoria__tipo', 'categoria__orden', 'orden', 'titulo']
        unique_together = ['categoria', 'slug']
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.titulo}"
    
    def get_absolute_url(self):
        return reverse('documentacion:documento', kwargs={
            'categoria_slug': self.categoria.slug,
            'documento_slug': self.slug
        })
    
    def get_contenido_html(self):
        """Convierte el markdown a HTML"""
        try:
            ruta_completa = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                self.archivo_markdown
            )
            
            with open(ruta_completa, 'r', encoding='utf-8') as archivo:
                contenido_md = archivo.read()
                
            # Convertir markdown a HTML con extensiones
            html = markdown.markdown(
                contenido_md,
                extensions=[
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.toc',
                    'markdown.extensions.codehilite',
                ]
            )
            return html
            
        except FileNotFoundError:
            return f"<p><strong>Error:</strong> No se encontró el archivo {self.archivo_markdown}</p>"
        except Exception as e:
            return f"<p><strong>Error:</strong> {str(e)}</p>"
    
    def puede_acceder(self, user):
        """Verifica si un usuario puede acceder a este documento"""
        if not self.publicado:
            return False
            
        if not user.is_authenticated:
            return False
            
        # Si no hay grupos específicos, todos los autenticados pueden acceder
        if not self.categoria.grupos_permitidos.exists():
            return True
            
        # Verificar si el usuario pertenece a algún grupo permitido
        return self.categoria.grupos_permitidos.filter(
            id__in=user.groups.values_list('id', flat=True)
        ).exists()


class HistorialAcceso(models.Model):
    """Registro de accesos a la documentación para analytics"""
    
    documento = models.ForeignKey(
        DocumentoMarkdown, 
        on_delete=models.CASCADE,
        verbose_name="Documento"
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    fecha_acceso = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de acceso")
    ip_address = models.GenericIPAddressField(verbose_name="IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Historial de Acceso"
        verbose_name_plural = "Historial de Accesos"
        ordering = ['-fecha_acceso']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.documento.titulo} ({self.fecha_acceso})"


class FeedbackDocumentacion(models.Model):
    """Sistema de feedback para mejorar la documentación"""
    
    TIPOS_FEEDBACK = [
        ('util', '👍 Útil'),
        ('no_util', '👎 No útil'),
        ('incorrecto', '❌ Información incorrecta'),
        ('falta_info', '❓ Falta información'),
        ('sugerencia', '💡 Sugerencia'),
    ]
    
    documento = models.ForeignKey(
        DocumentoMarkdown, 
        on_delete=models.CASCADE,
        verbose_name="Documento"
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    tipo = models.CharField(max_length=20, choices=TIPOS_FEEDBACK, verbose_name="Tipo")
    comentario = models.TextField(blank=True, verbose_name="Comentario")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    procesado = models.BooleanField(default=False, verbose_name="Procesado")
    
    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"
        ordering = ['-fecha']
        unique_together = ['documento', 'usuario']  # Un feedback por usuario por documento
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.documento.titulo} por {self.usuario.username}"
