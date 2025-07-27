from django.urls import path
from .views import custom_login
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', custom_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]