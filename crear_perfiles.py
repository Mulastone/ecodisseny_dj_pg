#!/usr/bin/env python
"""
Script para crear usuarios y perfiles para los recursos existentes
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecodisseny.settings')
django.setup()

from django.contrib.auth.models import User
from maestros.models import Recurso
from carregahores.models import PerfilUsuario
from django.db import transaction

def crear_usuarios_y_perfiles():
    print("=== CREANDO USUARIOS Y PERFILES ===")
    
    # Definir usuarios y sus recursos
    usuarios_recursos = [
        ('gonzalo', 2, True),   # (username, recurso_id, is_admin)
        ('sarah', 3, False),
        ('pilar', 4, False),
        ('santiago', 5, False),
        ('roger', 6, False)
    ]
    
    with transaction.atomic():
        # Limpiar datos existentes usando SQL directo
        print("Limpiando datos existentes...")
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Eliminar todos los registros de perfiles
            cursor.execute('DELETE FROM carregahores_perfilusuario;')
            cursor.execute('DELETE FROM carregahores_carregahores;')
            
            # Eliminar usuarios excepto mulastone
            cursor.execute("DELETE FROM auth_user WHERE username != 'mulastone';")
            
            # Resetear secuencias
            cursor.execute("SELECT setval('carregahores_perfilusuario_id_seq', 1, false);")
            cursor.execute("SELECT setval('carregahores_carregahores_id_seq', 1, false);")
            cursor.execute("SELECT setval('auth_user_id_seq', (SELECT COALESCE(MAX(id), 1) FROM auth_user));")
            
            print("Limpieza SQL completada")
        
        for username, recurso_id, is_admin in usuarios_recursos:
            try:
                # Obtener recurso
                recurso = Recurso.objects.get(id=recurso_id)
                
                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@ecodisseny.com',
                    password='ecodisseny2024',
                    first_name=recurso.nom,
                    is_active=True,
                    is_staff=is_admin,
                    is_superuser=is_admin
                )
                
                # Crear perfil
                perfil = PerfilUsuario.objects.create(
                    user=user,
                    recurso=recurso
                )
                
                admin_status = 'ADMIN' if is_admin else 'USER'
                print(f'✓ Creado: {username} ({admin_status}) -> {recurso.nom}')
                
            except Exception as e:
                print(f'✗ Error creando {username}: {e}')
                raise
    
    print("\n=== VERIFICACIÓN FINAL ===")
    for perfil in PerfilUsuario.objects.all():
        admin_status = 'ADMIN' if perfil.user.is_superuser else 'USER'
        print(f'{perfil.user.username} ({admin_status}) -> {perfil.recurso.nom}')
    
    print(f"\nTotal usuarios: {User.objects.count()}")
    print(f"Total perfiles: {PerfilUsuario.objects.count()}")
    
    print("\n=== CONTRASEÑAS ===")
    print("Todos los usuarios tienen la contraseña: ecodisseny2024")
    print("Usuarios admin: mulastone, gonzalo")

if __name__ == '__main__':
    crear_usuarios_y_perfiles()
