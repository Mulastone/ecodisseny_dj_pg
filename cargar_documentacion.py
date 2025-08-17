#!/usr/bin/env python3
"""
Script para cargar automáticamente los documentos markdown existentes en la base de datos.
Debe ejecutarse desde la raíz del proyecto Django.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecodisseny.settings')
django.setup()

from django.contrib.auth.models import User, Group
from documentacion.models import CategoriaDocumentacion, DocumentoMarkdown
from django.utils.text import slugify


def crear_categorias():
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
            print(f"✅ Categoría creada: {categoria.nombre}")
        else:
            print(f"ℹ️  Categoría ya existe: {categoria.nombre}")
    
    return categorias


def cargar_documentos():
    """Cargar los documentos markdown existentes"""
    
    # Obtener el usuario Axel o el admin para asignar como autor
    try:
        admin_user = User.objects.filter(first_name__icontains='axel').first()
        if not admin_user:
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                admin_user.first_name = 'Axel'
                admin_user.last_name = 'Rasmussen'
                admin_user.save()
                print(f"✅ Usuario actualizado: {admin_user.username} -> Axel Rasmussen")
        
        if not admin_user:
            admin_user = User.objects.create_superuser('axel', 'axel@ecodisseny.com', 'admin123')
            admin_user.first_name = 'Axel'
            admin_user.last_name = 'Rasmussen'
            admin_user.save()
            print(f"✅ Usuario creado: Axel Rasmussen")
    except Exception as e:
        print(f"⚠️  Error configurando usuario: {e}")
        admin_user = None
    
    # Buscar automáticamente todos los archivos .md en docs/
    import glob
    
    documentos = []
    docs_base = os.path.join(os.path.dirname(__file__), 'docs')
    
    # Buscar todos los archivos .md
    md_files = glob.glob(os.path.join(docs_base, '**/*.md'), recursive=True)
    
    for archivo_path in md_files:
        # Obtener ruta relativa
        archivo_relativo = os.path.relpath(archivo_path, os.path.dirname(__file__))
        
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
    
    print(f"📁 Encontrados {len(documentos)} archivos de documentación")
    
    documentos_creados = 0
    documentos_existentes = 0
    
    for doc_data in documentos:
        # Obtener la categoría
        try:
            categoria = CategoriaDocumentacion.objects.get(slug=doc_data['categoria_slug'])
        except CategoriaDocumentacion.DoesNotExist:
            print(f"❌ Categoría no encontrada: {doc_data['categoria_slug']}")
            continue
        
        # Verificar si el archivo existe
        archivo_path = os.path.join(os.path.dirname(__file__), doc_data['archivo_markdown'])
        if not os.path.exists(archivo_path):
            print(f"⚠️  Archivo no encontrado: {doc_data['archivo_markdown']}")
            continue
        
        # Crear slug del documento
        doc_slug = slugify(doc_data['titulo'])
        
        # Verificar si el documento ya existe
        documento, created = DocumentoMarkdown.objects.get_or_create(
            categoria=categoria,
            slug=doc_slug,
            defaults={
                'titulo': doc_data['titulo'],
                'archivo_markdown': doc_data['archivo_markdown'],
                'resumen': doc_data['resumen'],
                'palabras_clave': doc_data['palabras_clave'],
                'destacado': doc_data.get('destacado', False),
                'orden': doc_data.get('orden', 0),
                'autor': admin_user,
                'publicado': True,
            }
        )
        
        if created:
            print(f"✅ Documento creado: {doc_data['titulo']} -> {doc_data['archivo_markdown']}")
            documentos_creados += 1
        else:
            print(f"ℹ️  Documento ya existe: {doc_data['titulo']}")
            documentos_existentes += 1
    
    print(f"\n📊 Resumen:")
    print(f"   • Documentos creados: {documentos_creados}")
    print(f"   • Documentos existentes: {documentos_existentes}")


def main():
    print("🚀 Iniciando carga de documentación...")
    print("\n1️⃣ Creando categorías...")
    crear_categorias()
    
    print("\n2️⃣ Cargando documentos...")
    cargar_documentos()
    
    print("\n✅ ¡Proceso completado!")
    print("\n📝 Ahora puedes:")
    print("   • Acceder a /documentacion/ en tu aplicación")
    print("   • Gestionar documentos desde el admin de Django")
    print("   • Añadir más documentos creando archivos .md y registrándolos")


if __name__ == '__main__':
    main()
