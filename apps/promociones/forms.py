from django import forms
from .models import Promocion


class PromocionGestionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = [
            "parrilla",
            "titulo",
            "descripcion",
            "precio_promocional",
            "fecha_inicio",
            "fecha_fin",
            "is_active",
        ]
        widgets = {
            "parrilla": forms.Select(attrs={"class": "gestion-form-input"}),
            "titulo": forms.TextInput(attrs={"class": "gestion-form-input"}),
            "descripcion": forms.Textarea(attrs={"class": "gestion-form-input", "rows": 4}),
            "precio_promocional": forms.NumberInput(
                attrs={"class": "gestion-form-input", "step": "0.01", "min": "0"}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"class": "gestion-form-input", "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"class": "gestion-form-input", "type": "date"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "gestion-form-checkbox"}),
        }