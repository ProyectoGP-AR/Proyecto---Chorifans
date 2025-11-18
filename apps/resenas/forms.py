from django import forms
from .models import Resena

class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ["puntaje", "comentario"]

        widgets = {
            "puntaje": forms.Select(attrs={
                "class": "form-input",
            }),
            "comentario": forms.Textarea(attrs={
                "class": "form-textarea",
                "rows": 4,
                "placeholder": "Contanos tu experiencia…"
            }),
        }

