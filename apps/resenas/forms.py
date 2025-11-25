from django import forms

from .models import Resena, RespuestaResena


class ResenaForm(forms.ModelForm):
    """
    Formulario para que un usuario común deje una reseña
    (puntaje + comentario) sobre una parrilla.
    """

    class Meta:
        model = Resena
        fields = ["puntaje", "comentario"]

        widgets = {
            "puntaje": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "comentario": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Contanos tu experiencia…",
                }
            ),
        }


class RespuestaResenaForm(forms.ModelForm):
    """
    Formulario para que la parrilla responda a una reseña
    y elija una valoración (carita feliz o triste).
    Lo usan los usuarios dueños de parrilla desde el panel
    'Valorar reseñas'.
    """

    class Meta:
        model = RespuestaResena
        fields = ["texto", "valoracion"]

        widgets = {
            "valoracion": forms.Select(
                attrs={
                    "class": "form-input",  
                }
            ),
            "texto": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Escribí la respuesta oficial de la parrilla…",
                }
            ),
        }

        labels = {
            "texto": "Respuesta de la parrilla",
            "valoracion": "Valoración de la reseña",
        }
