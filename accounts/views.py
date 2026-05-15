from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone

def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Mensaje de bienvenida personalizado
            if user.is_superuser:
                messages.success(request, f'Benvingut/da {user.get_full_name() or user.username}! Tens accés complet al sistema.')
                return redirect('home')  # Todos van a la página de inicio
            else:
                messages.success(request, f'Benvingut/da {user.get_full_name() or user.username}! Pots començar a carregar les teves hores.')
                return redirect('home')  # Todos van a la página de inicio
        else:
            messages.error(request, 'Credencials incorrectes. Comprova el nom d\'usuari i la contrasenya.')
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

@login_required
def redirect_after_login(request):
    """
    Vista auxiliar para redirección inteligente después del login
    """
    user = request.user
    
    if user.is_superuser:
        messages.success(request, f'Benvingut/da {user.get_full_name() or user.username}! Tens accés complet al sistema.')
        return redirect('home')
    else:
        messages.success(request, f'Benvingut/da {user.get_full_name() or user.username}! Pots començar a carregar les teves hores.')
        return redirect('home')

@login_required
def profile_view(request):
    """
    Vista del perfil de usuario
    """
    user = request.user
    context = {
        'user': user,
        'title': 'Perfil d\'Usuari'
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def change_password_view(request):
    """
    Vista para cambiar la contraseña
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'La teva contrasenya s\'ha actualitzat correctament!')
            return redirect('profile')
        else:
            messages.error(request, 'Si us plau, corregeix els errors a continuació.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Canviar Contrasenya'
    }
    return render(request, 'accounts/change_password.html', context)


def home_view(request):
    context = {}
    if request.user.is_authenticated:
        from carregahores.models import CarregaHores
        from pressupostos.models import Pressupost
        from django.contrib.auth import get_user_model

        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())

        if request.user.is_superuser:
            User = get_user_model()
            from django.db.models import Sum
            hores_setmana = CarregaHores.objects.filter(data__gte=week_start).aggregate(total=Sum('hores'))['total']
            context['stat_hores_avui'] = CarregaHores.objects.filter(data=today).count()
            context['stat_hores_setmana'] = hores_setmana or 0
            context['stat_pressupostos'] = Pressupost.objects.count()
            context['stat_usuaris'] = User.objects.filter(is_active=True).count()
        else:
            from django.db.models import Sum
            context['stat_hores_setmana'] = CarregaHores.objects.filter(
                usuari=request.user, data__gte=week_start
            ).aggregate(total=Sum('hores'))['total'] or 0
            context['stat_hores_mes'] = CarregaHores.objects.filter(
                usuari=request.user, data__year=today.year, data__month=today.month
            ).aggregate(total=Sum('hores'))['total'] or 0
            context['stat_carregues_total'] = CarregaHores.objects.filter(usuari=request.user).count()

    return render(request, 'index.html', context)