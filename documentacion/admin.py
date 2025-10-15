from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.forms import Textarea
from django import forms
from .models import CategoriaDocumentacion, DocumentoMarkdown, HistorialAcceso
import os


class DocumentoMarkdownForm(forms.ModelForm):
    contenido_markdown = forms.CharField(
        widget=Textarea(attrs={
            'rows': 30, 
            'cols': 120,
            'style': 'font-family: monospace; font-size: 14px;'
        }),
        label='Contenido Markdown',
        required=False,
        help_text='Edita el contenido del archivo markdown directamente aquí'
    )
    
    class Meta:
        model = DocumentoMarkdown
        fields = '__all__'
        widgets = {
            'categoria': forms.Select(attrs={'style': 'width: 100%;'}),
            'resumen': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que las categorías se muestren correctamente
        self.fields['categoria'].queryset = CategoriaDocumentacion.objects.filter(activa=True).order_by('tipo', 'nombre')
        
        if self.instance and self.instance.pk:
            try:
                with open(self.instance.archivo_markdown, 'r', encoding='utf-8') as f:
                    self.fields['contenido_markdown'].initial = f.read()
            except FileNotFoundError:
                self.fields['contenido_markdown'].initial = f"# Error: Archivo no encontrado\n\nEl archivo {self.instance.archivo_markdown} no existe.\n\nPuedes crear contenido aquí y se guardará automáticamente."
            except Exception as e:
                self.fields['contenido_markdown'].initial = f"# Error al cargar archivo\n\nError: {str(e)}"
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit and 'contenido_markdown' in self.cleaned_data:
            contenido = self.cleaned_data['contenido_markdown']
            if contenido:
                # Crear directorio si no existe
                import os
                os.makedirs(os.path.dirname(instance.archivo_markdown), exist_ok=True)
                
                # Guardar contenido en archivo
                with open(instance.archivo_markdown, 'w', encoding='utf-8') as f:
                    f.write(contenido)
        return instance


@admin.register(CategoriaDocumentacion)
class CategoriaDocumentacionAdmin(admin.ModelAdmin):
    list_display = ('icono_nombre', 'tipo', 'documentos_count', 'activa', 'orden')
    list_filter = ('tipo', 'activa')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('orden', 'activa')
    prepopulated_fields = {'slug': ('nombre',)}
    filter_horizontal = ('grupos_permitidos',)
    
    # Configuraciones para mejorar la visualización
    list_per_page = 25
    save_on_top = True
    
    fieldsets = (
        ('📝 Informació Bàsica', {
            'fields': ('nombre', 'slug', 'descripcion', 'icono')
        }),
        ('🎯 Configuració', {
            'fields': ('tipo', 'orden', 'activa')
        }),
        ('🔐 Permisos', {
            'fields': ('grupos_permitidos',),
            'classes': ('collapse',)
        })
    )
    
    def icono_nombre(self, obj):
        return format_html('{} {}', obj.icono, obj.nombre)
    icono_nombre.short_description = 'Categoria'
    
    def documentos_count(self, obj):
        count = obj.documentos.count()
        if count > 0:
            url = reverse('admin:documentacion_documentomarkdown_changelist')
            return format_html('<a href="{}?categoria__id__exact={}">{} docs</a>', url, obj.id, count)
        return '0 docs'
    documentos_count.short_description = 'Documents'


@admin.register(DocumentoMarkdown)
class DocumentoMarkdownAdmin(admin.ModelAdmin):
    form = DocumentoMarkdownForm
    list_display = ('titulo', 'categoria_info', 'archivo_status', 'publicado', 'destacado', 'accesos_count', 'fecha_actualizacion')
    list_filter = ('categoria', 'publicado', 'destacado', 'fecha_creacion', 'fecha_actualizacion')
    search_fields = ('titulo', 'resumen', 'palabras_clave', 'archivo_markdown')
    list_editable = ('publicado', 'destacado')
    readonly_fields = ('slug', 'fecha_creacion', 'fecha_actualizacion', 'contenido_preview', 'archivo_info')
    
    fieldsets = (
        ('📝 Informació Principal', {
            'fields': ('titulo', 'slug', 'categoria', 'resumen')
        }),
        ('📁 Arxiu', {
            'fields': ('archivo_markdown', 'archivo_info'),
            'description': 'Ruta relativa des de l’arrel del projecte'
        }),
        ('✏️ Editor de Contingut', {
            'fields': ('contenido_markdown',),
            'description': 'Edita el contingut markdown directament des d’aquí'
        }),
        ('🎯 Configuració', {
            'fields': ('orden', 'publicado', 'destacado', 'autor')
        }),
        ('🔍 SEO i Cerca', {
            'fields': ('palabras_clave',),
            'classes': ('collapse',)
        }),
        ('📊 Metadades', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
        ('👁️ Vista Prèvia', {
            'fields': ('contenido_preview',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['marcar_como_publicado', 'marcar_como_no_publicado', 'marcar_como_destacado', 'quitar_destacado', 'verificar_archivos']
    
    def categoria_info(self, obj):
        return format_html('{} {}', obj.categoria.icono, obj.categoria.nombre)
    categoria_info.short_description = 'Categoria'
    
    def archivo_status(self, obj):
        if os.path.exists(obj.archivo_markdown):
            size = os.path.getsize(obj.archivo_markdown)
            size_kb = round(size / 1024, 1)
            return format_html(
                '<span style="color: green;">✅ {} KB</span>', 
                size_kb
            )
        else:
            return format_html('<span style="color: red;">❌ No existe</span>')
    archivo_status.short_description = 'Arxiu'
    
    def accesos_count(self, obj):
        count = obj.accesos.count()
        if count > 0:
            url = reverse('admin:documentacion_historialacceso_changelist')
            return format_html('<a href="{}?documento__id__exact={}">{} accesos</a>', url, obj.id, count)
        return '0'
    accesos_count.short_description = 'Accesos'
    
    def archivo_info(self, obj):
        if obj.archivo_markdown:
            if os.path.exists(obj.archivo_markdown):
                stat = os.stat(obj.archivo_markdown)
                size = round(stat.st_size / 1024, 1)
                from datetime import datetime
                modified = datetime.fromtimestamp(stat.st_mtime)
                return format_html(
                    '<div style="font-family: monospace;">'
                    '<strong>📁 Archivo:</strong> {}<br>'
                    '<strong>📏 Tamaño:</strong> {} KB<br>'
                    '<strong>📅 Modificado:</strong> {}<br>'
                    '<strong>🔗 URL:</strong> <a href="{}" target="_blank">Ver documento</a>'
                    '</div>',
                    obj.archivo_markdown,
                    size,
                    modified.strftime('%Y-%m-%d %H:%M'),
                    obj.get_absolute_url()
                )
            else:
                return format_html(
                    '<div style="color: red; font-weight: bold;">'
                    '❌ Archivo no encontrado: {}'
                    '</div>',
                    obj.archivo_markdown
                )
        return 'No especificado'
    archivo_info.short_description = 'Informació de l’Arxiu'
    
    def contenido_preview(self, obj):
        try:
            # Obtener contenido HTML renderizado
            contenido_html = obj.get_contenido_html()
            contenido_markdown = obj.obtener_contenido()
            
            if contenido_html and contenido_markdown:
                # Limitar el contenido para preview
                if len(contenido_html) > 2000:
                    contenido_html = contenido_html[:2000] + '<p><em>... (contenido truncado para preview)</em></p>'
                
                if len(contenido_markdown) > 1000:
                    contenido_markdown = contenido_markdown[:1000] + '\n\n... (contenido truncado para preview)'
                
                return format_html(
                    '<div style="border: 1px solid #ddd; border-radius: 4px; overflow: hidden;">'
                    '<div style="background: #f0f0f0; padding: 10px; border-bottom: 1px solid #ddd;">'
                    '<strong>📖 Vista Previa del Documento</strong>'
                    '<div style="float: right; font-size: 12px;">'
                    '<button type="button" onclick="togglePreview(this)" style="margin-left: 10px; padding: 2px 8px; font-size: 11px;">🔄 Ver Markdown</button>'
                    '</div>'
                    '</div>'
                    '<div id="preview-html" style="max-height: 400px; overflow-y: auto; padding: 15px; background: white; line-height: 1.6;">'
                    '{}'
                    '</div>'
                    '<div id="preview-markdown" style="max-height: 400px; overflow-y: auto; padding: 15px; background: #f8f8f8; font-family: monospace; font-size: 13px; display: none; white-space: pre-wrap;">'
                    '{}'
                    '</div>'
                    '<script>'
                    'function togglePreview(btn) {{'
                    '  var htmlDiv = document.getElementById("preview-html");'
                    '  var mdDiv = document.getElementById("preview-markdown");'
                    '  if (htmlDiv.style.display === "none") {{'
                    '    htmlDiv.style.display = "block";'
                    '    mdDiv.style.display = "none";'
                    '    btn.textContent = "🔄 Ver Markdown";'
                    '  }} else {{'
                    '    htmlDiv.style.display = "none";'
                    '    mdDiv.style.display = "block";'
                    '    btn.textContent = "🔄 Ver HTML";'
                    '  }}'
                    '}}'
                    '</script>'
                    '</div>',
                    mark_safe(contenido_html),
                    contenido_markdown
                )
            return 'No se pudo cargar el contenido'
        except Exception as e:
            return format_html('<div style="color: red; padding: 10px;">❌ Error: {}</div>', str(e))
    contenido_preview.short_description = 'Vista Prèvia del Contingut'
    
    def marcar_como_publicado(self, request, queryset):
        updated = queryset.update(publicado=True)
        self.message_user(request, f'✅ {updated} documento(s) marcado(s) como publicado(s).')
    marcar_como_publicado.short_description = '✅ Marcar com a publicat'
    
    def marcar_como_no_publicado(self, request, queryset):
        updated = queryset.update(publicado=False)
        self.message_user(request, f'❌ {updated} documento(s) marcado(s) como no publicado(s).')
    marcar_como_no_publicado.short_description = '❌ Marcar com a no publicat'
    
    def marcar_como_destacado(self, request, queryset):
        updated = queryset.update(destacado=True)
        self.message_user(request, f'⭐ {updated} documento(s) marcado(s) como destacado(s).')
    marcar_como_destacado.short_description = '⭐ Marcar com a destacat'
    
    def quitar_destacado(self, request, queryset):
        updated = queryset.update(destacado=False)
        self.message_user(request, f'⚪ {updated} documento(s) ya no están destacados.')
    quitar_destacado.short_description = '⚪ Treure destacat'
    
    def verificar_archivos(self, request, queryset):
        existentes = 0
        faltantes = 0
        for doc in queryset:
            if os.path.exists(doc.archivo_markdown):
                existentes += 1
            else:
                faltantes += 1

        mensaje = f'Verificación: {existentes} archivos existents, {faltantes} no trobats.'
        if faltantes > 0:
            self.message_user(request, mensaje, level='WARNING')
        else:
            self.message_user(request, mensaje)
    verificar_archivos.short_description = 'Verificar arxius físics'
    
    def save_model(self, request, obj, form, change):
        # Si es un documento nuevo y no tiene autor, asignar el usuario actual
        if not change and not obj.autor:
            obj.autor = request.user
        super().save_model(request, obj, form, change)


@admin.register(HistorialAcceso)
class HistorialAccesoAdmin(admin.ModelAdmin):
    list_display = ('documento_link', 'usuario', 'ip_address', 'fecha_acceso', 'user_agent_short')
    list_filter = ('fecha_acceso', 'documento__categoria')
    search_fields = ('documento__titulo', 'usuario__username', 'ip_address')
    readonly_fields = ('documento', 'usuario', 'ip_address', 'user_agent', 'fecha_acceso')
    date_hierarchy = 'fecha_acceso'
    
    def has_add_permission(self, request):
        return False  # No permitir crear manualmente
    
    def documento_link(self, obj):
        url = reverse('admin:documentacion_documentomarkdown_change', args=[obj.documento.id])
        return format_html('<a href="{}">{}</a>', url, obj.documento.titulo)
    documento_link.short_description = 'Document'
    
    def user_agent_short(self, obj):
        if obj.user_agent:
            # Mostrar solo los primeros 50 caracteres
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'
    user_agent_short.short_description = 'Navegador'


# Personalizar el admin site
admin.site.site_header = "📚 Ecodisseny - Administració de Documentació"
admin.site.site_title = "Documentació Admin"
admin.site.index_title = "Gestió de Documentació"
