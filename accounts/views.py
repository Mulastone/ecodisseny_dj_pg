from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('pressupostos:list')  # Cambia por tu vista principal
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})