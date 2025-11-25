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
