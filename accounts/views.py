from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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