from django import forms
from .models import Categoria


class CategoriaGestionForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = [
            "nombre",
            "slug",
            "descripcion",
            "is_active",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "gestion-form-input"}),
            "slug": forms.TextInput(attrs={"class": "gestion-form-input"}),
            "descripcion": forms.Textarea(attrs={"class": "gestion-form-input", "rows": 4}),
            "is_active": forms.CheckboxInput(attrs={"class": "gestion-form-checkbox"}),
        }