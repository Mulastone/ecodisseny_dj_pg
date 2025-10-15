from django.db import models
from django.contrib.auth.models import User, Group
from django.urls import reverse
import markdown
import os


class CategoriaDocumentacion(models.Model):
    """Categorías de documentación según tipo de usuario"""
    
    TIPOS_CATEGORIA = [
        ('usuario', '👤 Usuari'),
        ('admin', '🔧 Administrador'), 
        ('dev', '🛠️ Desenvolupador'),
        ('general', '📚 General'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="URL amigable")
    tipo = models.CharField(max_length=20, choices=TIPOS_CATEGORIA, verbose_name="Tipus")
    descripcion = models.TextField(blank=True, verbose_name="Descripció")
    icono = models.CharField(max_length=50, default="📚", verbose_name="Icona")
    orden = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    
    # Permisos d'accés
    grupos_permitidos = models.ManyToManyField(
        Group, 
        blank=True, 
        verbose_name="Grups amb accés",
        help_text="Si no s'especifica, tots els usuaris autenticats tenen accés"
    )
    
    class Meta:
        verbose_name = "Categoria de Documentació"
        verbose_name_plural = "Categories de Documentació"
        ordering = ['tipo', 'orden', 'nombre']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"


class DocumentoMarkdown(models.Model):
    """Documento de documentación en formato Markdown"""
    
    titulo = models.CharField(max_length=200, verbose_name="Títol")
    slug = models.SlugField(verbose_name="URL amigable")
    categoria = models.ForeignKey(
        CategoriaDocumentacion, 
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name="Categoria"
    )
    
    # Contingut
    archivo_markdown = models.CharField(
        max_length=500, 
        verbose_name="Ruta de l'arxiu .md",
        help_text="Exemple: docs/usuari/inici-rapid.md"
    )
    resumen = models.TextField(blank=True, verbose_name="Resum")
    
    # Metadades
    orden = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creat")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Actualitzat")
    autor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Autor"
    )
    
    # Configuració
    publicado = models.BooleanField(default=True, verbose_name="Publicat")
    destacado = models.BooleanField(default=False, verbose_name="Destacat")
    
    # SEO i cerca
    palabras_clave = models.CharField(
        max_length=500, 
        blank=True, 
        verbose_name="Paraules clau",
        help_text="Separades per comes"
    )
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['categoria__tipo', 'categoria__orden', 'orden', 'titulo']
        unique_together = ['categoria', 'slug']
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.titulo}"
    
    def get_absolute_url(self):
        return reverse('documentacion:documento', kwargs={
            'categoria_slug': self.categoria.slug,
            'documento_slug': self.slug
        })
    
    def obtener_contenido(self):
        """Obtiene el contenido markdown raw del archivo"""
        try:
            with open(self.archivo_markdown, 'r', encoding='utf-8') as archivo:
                return archivo.read()
        except FileNotFoundError:
            return f"Error: No se encontró el archivo {self.archivo_markdown}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_contenido_html(self):
        """Convierte el markdown a HTML"""
        try:
            with open(self.archivo_markdown, 'r', encoding='utf-8') as archivo:
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
        related_name='accesos',
        verbose_name="Document"
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuari"
    )
    fecha_acceso = models.DateTimeField(auto_now_add=True, verbose_name="Data d'accés")
    ip_address = models.GenericIPAddressField(verbose_name="IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Historial d'Accés"
        verbose_name_plural = "Historials d'Accés"
        ordering = ['-fecha_acceso']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.documento.titulo} ({self.fecha_acceso})"


class FeedbackDocumentacion(models.Model):
    """Sistema de feedback para mejorar la documentación"""
    
    TIPUS_FEEDBACK = [
        ('util', '👍 Útil'),
        ('no_util', '👎 No útil'),
        ('incorrecte', '❌ Informació incorrecta'),
        ('falta_info', '❓ Falta informació'),
        ('suggeriment', '💡 Suggeriment'),
    ]
    
    documento = models.ForeignKey(
        DocumentoMarkdown, 
        on_delete=models.CASCADE,
        verbose_name="Document"
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuari"
    )
    tipo = models.CharField(max_length=20, choices=TIPUS_FEEDBACK, verbose_name="Tipus")
    comentario = models.TextField(blank=True, verbose_name="Comentari")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Data")
    procesado = models.BooleanField(default=False, verbose_name="Processat")
    
    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"
        ordering = ['-fecha']
        unique_together = ['documento', 'usuario']  # Un feedback per usuari per document
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.documento.titulo} por {self.usuario.username}"
