from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

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