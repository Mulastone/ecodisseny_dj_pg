from django import forms
from .models import Clients


class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = '__all__'
