from django.urls import path
from .views import custom_login, redirect_after_login, profile_view, change_password_view
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path('login/', custom_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('redirect/', redirect_after_login, name='redirect_after_login'),
    
    # User profile and password change
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
    
    # Password reset URLs
    path('password_reset/', PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]