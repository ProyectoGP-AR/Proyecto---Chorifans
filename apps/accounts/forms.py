from django import forms
from django.contrib.auth.models import User

from .models import Profile
from apps.parrillas.models import Parrilla


class UsuarioGestionForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "gestion-form-input"}),
        label="Nombre",
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "gestion-form-input"}),
        label="Apellido",
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "gestion-form-input"}),
        label="Email",
    )

    nickname = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "gestion-form-input"}),
        label="Nickname",
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "gestion-form-input", "rows": 4}),
        label="Bio",
    )
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "gestion-form-input"}),
        label="Teléfono",
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "gestion-form-input"}),
        label="Avatar",
    )

    es_duenio_parrilla = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "gestion-form-checkbox"}),
        label="Es dueño de parrilla",
    )
    parrilla_asociada = forms.ModelChoiceField(
        queryset=Parrilla.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "gestion-form-input"}),
        label="Parrilla asociada",
    )
    profile_is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "gestion-form-checkbox"}),
        label="Perfil activo",
    )

    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "gestion-form-checkbox"}),
        label="Usuario activo",
    )
    is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "gestion-form-checkbox"}),
        label="Administrador del panel",
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "gestion-form-input"}),
        label="Contraseña",
        help_text="Solo completá este campo si querés definir o cambiar la contraseña.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "password",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "gestion-form-input"}),
        }
        labels = {
            "username": "Nombre de usuario",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            profile, _ = Profile.objects.get_or_create(user=self.instance)

            self.fields["nickname"].initial = profile.nickname
            self.fields["bio"].initial = profile.bio
            self.fields["telefono"].initial = profile.telefono
            self.fields["avatar"].initial = profile.avatar
            self.fields["es_duenio_parrilla"].initial = profile.es_duenio_parrilla
            self.fields["parrilla_asociada"].initial = profile.parrilla_asociada
            self.fields["profile_is_active"].initial = profile.is_active

            self.fields["first_name"].initial = self.instance.first_name
            self.fields["last_name"].initial = self.instance.last_name
            self.fields["email"].initial = self.instance.email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data.get("email", "")
        user.is_active = self.cleaned_data.get("is_active", True)
        user.is_staff = self.cleaned_data.get("is_staff", False)

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.nickname = self.cleaned_data.get("nickname")
            profile.bio = self.cleaned_data.get("bio")
            profile.telefono = self.cleaned_data.get("telefono")
            profile.es_duenio_parrilla = self.cleaned_data.get("es_duenio_parrilla", False)
            profile.parrilla_asociada = self.cleaned_data.get("parrilla_asociada")
            profile.is_active = self.cleaned_data.get("profile_is_active", True)

            avatar = self.cleaned_data.get("avatar")
            if avatar:
                profile.avatar = avatar

            profile.save()

        return user