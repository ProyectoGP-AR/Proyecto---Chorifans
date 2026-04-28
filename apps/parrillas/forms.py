# apps/parrillas/forms.py

from django import forms


class BuscarParrillaForm(forms.Form):
    """
    Formulario simple (NO basado en modelo) para buscar parrillas.

    Lo vamos a usar con una vista basada en clases (FormView)
    para cumplir con:
      - Formulario en el front
      - Validación back-end
      - Form basado en clases (CBV)
    """

    termino = forms.CharField(
        label="Buscar parrilla",
        max_length=100,
        required=False,  # Permitimos que se envíe vacío
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Ej: choripán, Palermo, vegana…",
            }
        ),
    )


from .models import Parrilla


class ParrillaGestionForm(forms.ModelForm):
    class Meta:
        model = Parrilla
        fields = [
            "nombre",
            "descripcion",
            "direccion",
            "telefono",
            "sitio_web",
            "ubicacion",
            "categoria",
            "foto_principal",
            "promedio_puntaje",
            "is_active",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "gestion-form-input"}),
            "descripcion": forms.Textarea(attrs={"class": "gestion-form-input", "rows": 4}),
            "direccion": forms.TextInput(attrs={"class": "gestion-form-input"}),
            "telefono": forms.TextInput(attrs={"class": "gestion-form-input"}),
            "sitio_web": forms.URLInput(attrs={"class": "gestion-form-input"}),
            "ubicacion": forms.Select(attrs={"class": "gestion-form-input"}),
            "categoria": forms.Select(attrs={"class": "gestion-form-input"}),
            "foto_principal": forms.ClearableFileInput(attrs={"class": "gestion-form-input"}),
            "promedio_puntaje": forms.NumberInput(attrs={"class": "gestion-form-input", "step": "0.1", "min": "0", "max": "5"}),
            "is_active": forms.CheckboxInput(attrs={"class": "gestion-form-checkbox"}),
        }