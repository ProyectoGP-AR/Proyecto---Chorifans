from django import forms
from .models import Ubicacion


class UbicacionGestionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = [
            "nombre_ciudad",
            "nombre_barrio",
            "latitud",
            "longitud",
            "google_maps_url",
            "is_active",
        ]
        widgets = {
            "nombre_ciudad": forms.TextInput(attrs={"class": "gestion-form-input"}),
            "nombre_barrio": forms.TextInput(attrs={"class": "gestion-form-input"}),
            "latitud": forms.NumberInput(
                attrs={"class": "gestion-form-input", "step": "any"}
            ),
            "longitud": forms.NumberInput(
                attrs={"class": "gestion-form-input", "step": "any"}
            ),
            "google_maps_url": forms.URLInput(attrs={"class": "gestion-form-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "gestion-form-checkbox"}),
        }