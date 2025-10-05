from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import Group
from maestros.models import PerfilUsuario, Recurso

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un usuario.
    SIMPLIFICADO: Busca recursos por coincidencia de nombres.
    """
    if created:
        # Intentar encontrar recurso por coincidencia de nombres
        recurso = None
        
        # Buscar por username
        try:
            recurso = Recurso.objects.get(nom__iexact=instance.username)
        except Recurso.DoesNotExist:
            pass
        
        # Buscar por first_name si no encontró por username
        if not recurso and instance.first_name:
            try:
                recurso = Recurso.objects.get(nom__icontains=instance.first_name)
            except (Recurso.DoesNotExist, Recurso.MultipleObjectsReturned):
                pass
        
        # Crear perfil (siempre, aunque sea sin recurso)
        PerfilUsuario.objects.get_or_create(
            user=instance,
            defaults={'recurso': recurso}
        )
        
        # Si no es staff/superuser, añadir al grupo de recursos
        if not instance.is_staff and not instance.is_superuser:
            grupo_recursos, created = Group.objects.get_or_create(name='Recursos')
            instance.groups.add(grupo_recursos)

@receiver(post_save, sender=Recurso)
def asignar_recurso_automatico(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo recurso, intenta asignarlo automáticamente
    a usuarios existentes sin recurso asignado.
    SOLO PARA RECURSOS QUE NECESITAN USUARIO (intern y colaborador).
    """
    if created:
        if instance.necesita_usuario:  # Solo intern y colaborador
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Buscar usuarios sin recurso que coincidan con el nombre
            from django.db import models as django_models
            usuarios_candidatos = User.objects.filter(
                perfil__recurso__isnull=True
            ).filter(
                django_models.Q(username__iexact=instance.nom) |
                django_models.Q(first_name__icontains=instance.nom.split()[0])
            )
            
            for usuario in usuarios_candidatos:
                perfil = getattr(usuario, 'perfil', None)
                if perfil and not perfil.recurso:
                    perfil.recurso = instance
                    perfil.save()
                    print(f'✅ Auto-asignado: {usuario.username} → {instance.nom} ({instance.tipus_recurso.tipus})')
                    break  # Solo asignar al primero que coincida
        else:
            # Recurso externo u otro tipo
            print(f'ℹ️  Recurso {instance.tipus_recurso.tipus} creado: {instance.nom} (no necesita usuario automático)')
