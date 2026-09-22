from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class CadastroProfessorForm(UserCreationForm):

    first_name = forms.CharField(label="Nome completo", max_length=150, required=True,)

    email = forms.EmailField(label="E-mail",required=True)

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Já existe uma conta cadastrada com este e-mail."
                )

        return email

    class Meta: 
        model = User
        fields = [
            "first_name",
            "email",
            "username",
            "password1",
            "password2"
        ] 

        labels = {
            "username":"Usuário",
            }
class LoginProfessorForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário ou e-mail",
        widget=forms.TextInput(
            attrs={"autocomplete": "username"}

            ),
        )
    
    def clean(self):
                identificador = self.cleaned_data.get("username")

                if identificador:
                    usuario_por_nome = User.objects.filter(
                        username=identificador
                    ).exists()

                    if not usuario_por_nome:
                        usuarios_por_email = User.objects.filter(
                            email__iexact=identificador
                        )

                        if usuarios_por_email.count() ==1:
                            usuario = usuarios_por_email.get()
                            self.cleaned_data["username"] = usuario.get_username()

                return super().clean() 
    