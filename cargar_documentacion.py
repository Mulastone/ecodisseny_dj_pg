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
    
    # Obtener el usuario admin para asignar como autor
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@ecodisseny.com', 'admin123')
    except:
        admin_user = None
    
    # Mapeo de archivos a documentos
    documentos = [
        # Documentos de usuario
        {
            'categoria_slug': 'usuario',
            'titulo': 'Inicio Rápido',
            'archivo_markdown': 'docs/usuario/inicio-rapido.md',
            'resumen': 'Guía de inicio rápido para nuevos usuarios',
            'palabras_clave': 'inicio, tutorial, primeros pasos',
            'destacado': True,
            'orden': 1,
        },
        {
            'categoria_slug': 'usuario',
            'titulo': 'Gestión de Presupuestos',
            'archivo_markdown': 'docs/usuario/presupuestos.md',
            'resumen': 'Cómo crear y gestionar presupuestos en el sistema',
            'palabras_clave': 'presupuestos, costos, facturación',
            'orden': 2,
        },
        {
            'categoria_slug': 'usuario',
            'titulo': 'Gestión de Proyectos',
            'archivo_markdown': 'docs/usuario/proyectos.md',
            'resumen': 'Guía para la gestión de proyectos',
            'palabras_clave': 'proyectos, gestión, planificación',
            'orden': 3,
        },
        
        # Documentos de administrador
        {
            'categoria_slug': 'admin',
            'titulo': 'Configuración del Sistema',
            'archivo_markdown': 'docs/admin/configuracion.md',
            'resumen': 'Configuración inicial y avanzada del sistema',
            'palabras_clave': 'configuración, setup, administración',
            'destacado': True,
            'orden': 1,
        },
        {
            'categoria_slug': 'admin',
            'titulo': 'Gestión de Usuarios',
            'archivo_markdown': 'docs/admin/usuarios.md',
            'resumen': 'Cómo gestionar usuarios y permisos',
            'palabras_clave': 'usuarios, permisos, roles, grupos',
            'orden': 2,
        },
        
        # Documentos generales
        {
            'categoria_slug': 'general',
            'titulo': 'README Principal',
            'archivo_markdown': 'docs/README.md',
            'resumen': 'Información general del proyecto',
            'palabras_clave': 'readme, información, general',
            'orden': 1,
        },
        {
            'categoria_slug': 'general',
            'titulo': 'Solución de Problemas',
            'archivo_markdown': 'docs/troubleshooting.md',
            'resumen': 'Guía para resolver problemas comunes',
            'palabras_clave': 'problemas, errores, troubleshooting, soluciones',
            'destacado': True,
            'orden': 2,
        },
    ]
    
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
