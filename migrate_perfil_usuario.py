#!/usr/bin/env python
"""
Script para migrar PerfilUsuario de carregahores a maestros
Ejecutar ANTES de aplicar las migraciones de Django
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecodisseny.settings')
django.setup()

from django.db import connection

def migrate_perfil_usuario():
    """Migra los datos de PerfilUsuario de carregahores a maestros"""
    with connection.cursor() as cursor:
        print("🔄 Iniciando migración de PerfilUsuario...")
        
        # 1. Crear tabla en maestros (si no existe)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS maestros_perfilusuario (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
            recurso_id INTEGER REFERENCES maestros_recurso(id) ON DELETE RESTRICT
        );
        """)
        
        # 2. Copiar datos desde carregahores
        cursor.execute("""
        INSERT INTO maestros_perfilusuario (id, user_id, recurso_id)
        SELECT id, user_id, recurso_id 
        FROM carregahores_perfilusuario
        ON CONFLICT (user_id) DO NOTHING;
        """)
        
        # 3. Actualizar secuencia
        cursor.execute("""
        SELECT setval('maestros_perfilusuario_id_seq', 
               (SELECT COALESCE(MAX(id), 1) FROM maestros_perfilusuario));
        """)
        
        # 4. Verificar migración
        cursor.execute("SELECT COUNT(*) FROM maestros_perfilusuario;")
        count_maestros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM carregahores_perfilusuario;")
        count_carregahores = cursor.fetchone()[0]
        
        print(f"✅ Registros en maestros_perfilusuario: {count_maestros}")
        print(f"📊 Registros en carregahores_perfilusuario: {count_carregahores}")
        
        if count_maestros == count_carregahores:
            print("🎉 Migración completada exitosamente!")
        else:
            print("⚠️ Algunos registros no se migraron. Revisa los conflictos.")

if __name__ == "__main__":
    migrate_perfil_usuario()