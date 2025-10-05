#!/usr/bin/env python
"""
Script para crear usuarios y perfiles después de cargar fixtures
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecodisseny.settings')
django.setup()

from django.contrib.auth.models import User
from maestros.models import Recurso
from maestros.models import PerfilUsuario

def crear_superusuario_mulastone():
    """Crear el superusuario mulastone si no existe"""
    try:
        user, created = User.objects.get_or_create(
            username='mulastone',
            defaults={
                'email': 'mulastone@ecodisseny.com',
                'first_name': 'Mulastone',
                'last_name': 'Admin',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('Santom@E14')
            user.save()
            print("   ✓ Superusuario 'mulastone' creado con contraseña personalizada")
        else:
            # Actualizar contraseña si ya existe
            user.set_password('Santom@E14')
            user.save()
            print("   - Superusuario 'mulastone' ya existía, contraseña actualizada")
            
    except Exception as e:
        print(f"   ✗ Error creando superusuario mulastone: {e}")

def crear_usuarios_y_perfiles():
    print("🔑 Creando usuarios y perfiles...")
    
    # Crear superusuario mulastone primero
    crear_superusuario_mulastone()
    
    # Definir usuarios y sus recursos
    usuarios_recursos = [
        ('gonzalo', 'Gonzalo', True),   # (username, nombre_recurso, is_admin)
        ('sarah', 'Sarah', False),
        ('pilar', 'Pilar', False),
        ('santiago', 'Santiago', False),
        ('roger', 'Roger', False)
    ]
    
    for username, nombre_recurso, is_admin in usuarios_recursos:
        try:
            # Buscar el recurso por nombre
            recurso = Recurso.objects.get(nom=nombre_recurso)
            
            # Crear usuario si no existe
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@ecodisseny.com',
                    'password': 'pbkdf2_sha256$720000$dummy$dummy',  # Se cambiará abajo
                    'first_name': nombre_recurso,
                    'is_active': True,
                    'is_staff': is_admin,
                    'is_superuser': is_admin
                }
            )
            
            if user_created:
                # Establecer contraseña
                user.set_password('ecodisseny2024')
                user.save()
                admin_status = '🔑 ADMIN' if is_admin else '👤 USER'
                print(f'   ✓ Usuario creado: {username} ({admin_status})')
            else:
                print(f'   - Usuario {username} ya existía')
            
            # Crear perfil si no existe
            perfil, perfil_created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={'recurso': recurso}
            )
            
            if perfil_created:
                print(f'   ✓ Perfil creado: {username} → {recurso.nom}')
            else:
                print(f'   - Perfil {username} ya existía')
                
        except Recurso.DoesNotExist:
            print(f'   ✗ Error: Recurso "{nombre_recurso}" no encontrado para {username}')
        except Exception as e:
            print(f'   ✗ Error creando {username}: {e}')
    
    print("\n📋 Resumen final:")
    total_users = User.objects.count()
    total_admins = User.objects.filter(is_superuser=True).count()
    total_profiles = PerfilUsuario.objects.count()
    
    print(f"   • Total usuarios: {total_users}")
    print(f"   • Administradores: {total_admins}")
    print(f"   • Perfiles creados: {total_profiles}")
    print(f"   • Contraseña usuarios normales: ecodisseny2024")
    print(f"   • Contraseña mulastone: Santom@E14")
    
    print("\n👥 Usuarios creados:")
    for user in User.objects.all().order_by('username'):
        admin_status = '🔑 ADMIN' if user.is_superuser else '👤 USER'
        special_note = ' (Superusuario principal)' if user.username == 'mulastone' else ''
        print(f"   {admin_status} {user.username}{special_note}")

if __name__ == '__main__':
    crear_usuarios_y_perfiles()
