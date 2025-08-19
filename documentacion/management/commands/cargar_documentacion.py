from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from documentacion.models import CategoriaDocumentacion, DocumentoMarkdown
from django.utils.text import slugify
import os


class Command(BaseCommand):
    help = 'Carga la documentación markdown existente en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Actualizar documentos existentes',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando carga de documentación...')
        )
        
        # Crear categorías
        self.stdout.write('\n1️⃣ Creando categorías...')
        self.crear_categorias()
        
        # Cargar documentos
        self.stdout.write('\n2️⃣ Cargando documentos...')
        self.cargar_documentos(update=options['update'])
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ ¡Proceso completado!')
        )

    def crear_categorias(self):
        """Crear las categorías básicas de documentación"""
        categorias = [
            {
                'nombre': 'Documentación de Usuario',
                'slug': 'usuario',
                'tipo': 'usuario',
                'descripcion': 'Guías para usuarios finales del sistema',
                'orden': 1,
            },
            {
                'nombre': 'Documentación de Administrador',
                'slug': 'admin',
                'tipo': 'admin',
                'descripcion': 'Guías para administradores del sistema',
                'orden': 2,
            },
            {
                'nombre': 'Documentación de Desarrollador',
                'slug': 'dev',
                'tipo': 'dev',
                'descripcion': 'Documentación técnica para desarrolladores',
                'orden': 3,
            },
            {
                'nombre': 'Documentación General',
                'slug': 'general',
                'tipo': 'general',
                'descripcion': 'Documentación general del sistema',
                'orden': 4,
            },
        ]
        
        for cat_data in categorias:
            categoria, created = CategoriaDocumentacion.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f"✅ Categoría creada: {categoria.nombre}")
            else:
                self.stdout.write(f"ℹ️  Categoría ya existe: {categoria.nombre}")

    def cargar_documentos(self, update=False):
        """Cargar los documentos markdown existentes"""
        
        # Obtener el usuario Axel o el admin para asignar como autor
        admin_user = User.objects.filter(first_name__icontains='axel').first()
        if not admin_user:
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                admin_user.first_name = 'Axel'
                admin_user.last_name = 'Rasmussen'
                admin_user.save()
                self.stdout.write(f"✅ Usuario actualizado: {admin_user.username} -> Axel Rasmussen")
        
        # Buscar automáticamente todos los archivos .md en docs/
        import glob
        
        documentos = []
        docs_base = os.path.join('/app', 'docs')  # Para Docker
        
        # Buscar todos los archivos .md
        md_files = glob.glob(os.path.join(docs_base, '**/*.md'), recursive=True)
        
        for archivo_path in md_files:
            # Obtener ruta relativa
            archivo_relativo = os.path.relpath(archivo_path, '/app')
            
            # Determinar categoría basada en la estructura de carpetas
            if '/admin/' in archivo_relativo:
                categoria_slug = 'admin'
            elif '/usuario/' in archivo_relativo:
                categoria_slug = 'usuario'
            elif '/dev/' in archivo_relativo:
                categoria_slug = 'dev'
            else:
                categoria_slug = 'general'
            
            # Obtener título del nombre del archivo
            nombre_archivo = os.path.basename(archivo_path)
            titulo_base = nombre_archivo.replace('.md', '').replace('-', ' ').replace('_', ' ')
            titulo = titulo_base.title()
            
            # Configuraciones especiales para algunos archivos
            configuraciones_especiales = {
                'README.md': {
                    'titulo': 'README Principal',
                    'destacado': True,
                    'orden': 1
                },
                'inicio-rapido.md': {
                    'titulo': 'Inicio Rápido',
                    'destacado': True,
                    'orden': 1
                },
                'troubleshooting.md': {
                    'titulo': 'Solución de Problemas',
                    'destacado': True,
                    'orden': 10
                },
                'configuracion.md': {
                    'titulo': 'Configuración del Sistema',
                    'destacado': True,
                    'orden': 1
                }
            }
            
            config = configuraciones_especiales.get(nombre_archivo, {})
            titulo = config.get('titulo', titulo)
            
            documentos.append({
                'categoria_slug': categoria_slug,
                'titulo': titulo,
                'archivo_markdown': archivo_relativo,
                'resumen': f'Documentación sobre {titulo.lower()}',
                'palabras_clave': titulo.lower().replace(' ', ', '),
                'destacado': config.get('destacado', False),
                'orden': config.get('orden', 5),
            })
        
        self.stdout.write(f"📁 Encontrados {len(documentos)} archivos de documentación")
        
        documentos_creados = 0
        documentos_existentes = 0
        documentos_actualizados = 0
        
        for doc_data in documentos:
            # Obtener la categoría
            try:
                categoria = CategoriaDocumentacion.objects.get(slug=doc_data['categoria_slug'])
            except CategoriaDocumentacion.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"❌ Categoría no encontrada: {doc_data['categoria_slug']}")
                )
                continue
            
            # Verificar si el archivo existe
            archivo_path = os.path.join('/app', doc_data['archivo_markdown'])  # Para Docker
            if not os.path.exists(archivo_path):
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Archivo no encontrado: {doc_data['archivo_markdown']}")
                )
                continue
            
            # Crear slug del documento
            doc_slug = slugify(doc_data['titulo'])
            
            # Verificar si el documento ya existe
            defaults = {
                'titulo': doc_data['titulo'],
                'archivo_markdown': doc_data['archivo_markdown'],
                'resumen': doc_data['resumen'],
                'palabras_clave': doc_data['palabras_clave'],
                'destacado': doc_data.get('destacado', False),
                'orden': doc_data.get('orden', 0),
                'autor': admin_user,
                'publicado': True,
            }
            
            documento, created = DocumentoMarkdown.objects.get_or_create(
                categoria=categoria,
                slug=doc_slug,
                defaults=defaults
            )
            
            if created:
                self.stdout.write(f"✅ Documento creado: {doc_data['titulo']} -> {doc_data['archivo_markdown']}")
                documentos_creados += 1
            elif update:
                # Actualizar documento existente
                for key, value in defaults.items():
                    setattr(documento, key, value)
                documento.save()
                self.stdout.write(f"🔄 Documento actualizado: {doc_data['titulo']}")
                documentos_actualizados += 1
            else:
                self.stdout.write(f"ℹ️  Documento ya existe: {doc_data['titulo']}")
                documentos_existentes += 1
        
        self.stdout.write(f"\n📊 Resumen:")
        self.stdout.write(f"   • Documentos creados: {documentos_creados}")
        if update:
            self.stdout.write(f"   • Documentos actualizados: {documentos_actualizados}")
        self.stdout.write(f"   • Documentos existentes: {documentos_existentes}")
