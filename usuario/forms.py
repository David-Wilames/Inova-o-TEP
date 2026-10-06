from django import forms
from django.contrib.auth.hashers import check_password, make_password

from .models import Usuarios


class LoginProfessorForm(forms.Form):

    usuario = forms.CharField(
        label="Usuário ou e-mail",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Digite seu usuário ou e-mail",
                "autocomplete": "username",
            }
        ),
    )

    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Digite sua senha",
                "autocomplete": "current-password",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        usuario_digitado = cleaned_data.get("usuario")
        senha_digitada = cleaned_data.get("senha")

        if not usuario_digitado or not senha_digitada:
            return cleaned_data

        # Procura pelo username
        usuario = Usuarios.objects.filter(
            username=usuario_digitado
        ).first()

        # Se não encontrou, procura pelo e-mail
        if usuario is None:
            usuario = Usuarios.objects.filter(
                email__iexact=usuario_digitado
            ).first()

        # Usuário/e-mail não encontrado
        if usuario is None:
            raise forms.ValidationError(
                "Usuário ou e-mail não encontrado."
            )

        # Verifica a senha criptografada
        if not check_password(senha_digitada, usuario.senha):
            raise forms.ValidationError("Senha incorreta.")

        # Guarda o usuário encontrado
        self.usuario = usuario

        return cleaned_data


class CadastroProfessorForm(forms.ModelForm):

    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(),
        required=True,
    )

    class Meta:
        model = Usuarios

        fields = [  # noqa: RUF012
            "nome_completo",
            "email",
            "username",
            "senha",
        ]

        labels = {  # noqa: RUF012
            "nome_completo": "Nome completo",
            "email": "E-mail",
            "username": "Usuário",
            "senha": "Senha",
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        if Usuarios.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "Já existe uma conta cadastrada com este e-mail."
            )

        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)

        # Criptografa a senha antes de salvar
        usuario.senha = make_password(usuario.senha)

        usuario.perfil_de_acesso = "colaborador"

        if commit:
            usuario.save()

        return usuario

