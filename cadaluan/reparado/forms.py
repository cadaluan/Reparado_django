from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
import re


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'password']
