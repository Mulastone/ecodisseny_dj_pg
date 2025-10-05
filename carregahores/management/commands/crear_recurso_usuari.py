from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from maestros.models import PerfilUsuario, Recurso, TipusRecurso


class Command(BaseCommand):
    help = 'Crear usuario y perfil para un nuevo recurso'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nom d\'usuari')
        parser.add_argument('--first_name', type=str, help='Nom de pila')
        parser.add_argument('--last_name', type=str, help='Cognoms', default='')
        parser.add_argument('--email', type=str, help='Correu electrònic', default='')
        parser.add_argument('--password', type=str, help='Contrasenya', default='changeme123')
        parser.add_argument('--recurso_name', type=str, help='Nom del recurs')
        parser.add_argument('--tipo_recurso', type=str, help='Tipus de recurs (Intern/Colaborador/Extern)', default='Intern')
        parser.add_argument('--preu_hora', type=float, help='Preu per hora', default=20.0)
        parser.add_argument('--is_staff', action='store_true', help='Fer l\'usuari staff/admin')

    def handle(self, *args, **options):
        username = options['username']
        recurso_name = options['recurso_name']
        
        if not username or not recurso_name:
            self.stdout.write(
                self.style.ERROR('❌ Cal especificar --username i --recurso_name')
            )
            return

        try:
            # 1. Crear o obtener tipo de recurso
            tipo_recurso, created = TipusRecurso.objects.get_or_create(
                tipus=options['tipo_recurso']
            )
            if created:
                self.stdout.write(f'✅ Tipus de recurs creat: {tipo_recurso.tipus}')

            # 2. Crear recurso si no existe
            recurso, created = Recurso.objects.get_or_create(
                nom=recurso_name,
                defaults={
                    'tipus_recurso': tipo_recurso,
                    'preu_tancat': 0,  # Por defecto no es precio cerrado
                    'preu_hora': options['preu_hora']
                }
            )
            if created:
                self.stdout.write(f'✅ Recurs creat: {recurso.nom} - {recurso.preu_hora}€/h')
            else:
                self.stdout.write(f'ℹ️ Recurs ja existeix: {recurso.nom}')

            # 3. Crear usuario si no existe
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': options['first_name'] or recurso_name,
                    'last_name': options['last_name'],
                    'email': options['email'],
                    'is_staff': options['is_staff'],
                }
            )
            if created:
                user.set_password(options['password'])
                user.save()
                self.stdout.write(f'✅ Usuari creat: {user.username} (password: {options["password"]})')
            else:
                self.stdout.write(f'ℹ️ Usuari ja existeix: {user.username}')

            # 4. Crear perfil
            perfil, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={'recurso': recurso}
            )
            if created:
                self.stdout.write(f'✅ Perfil creat: {user.username} → {recurso.nom}')
            else:
                if perfil.recurso != recurso:
                    perfil.recurso = recurso
                    perfil.save()
                    self.stdout.write(f'🔄 Perfil actualitzat: {user.username} → {recurso.nom}')
                else:
                    self.stdout.write(f'ℹ️ Perfil ja correcte: {user.username} → {recurso.nom}')

            # Resumen
            self.stdout.write('\n=== RESUM ===')
            self.stdout.write(f'👤 Usuari: {user.username} ({user.get_full_name()})')
            self.stdout.write(f'📦 Recurs: {recurso.nom} ({recurso.tipus_recurso.tipus})')
            self.stdout.write(f'💰 Preu: {recurso.preu_hora}€/h')
            self.stdout.write(f'🔐 Permisos: {"Admin" if user.is_staff else "Usuari normal"}')
            
            if created:
                self.stdout.write(f'\n🎯 PROPER PAS: L\'usuari pot fer login amb:')
                self.stdout.write(f'   Username: {username}')
                self.stdout.write(f'   Password: {options["password"]}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )