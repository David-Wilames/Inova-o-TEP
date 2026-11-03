import pytest
from django.contrib.auth.hashers import check_password, make_password
from django.urls import reverse

from usuario.models import Usuarios


@pytest.fixture
def colaborador_existente(db):
    return Usuarios.objects.create(
        nome_completo="Colaborador Existente",
        email="existente@exemplo.com",
        username="colaborador_existente",
        senha=make_password("SenhaTeste123"),
        perfil_de_acesso="colaborador",
    )


@pytest.mark.django_db
def test_cadastro_com_dados_validos(client):
    resposta = client.post(
        reverse("cadastro_colaborador"),
        {
            "nome_completo": "Novo Colaborador",
            "email": "novo@exemplo.com",
            "username": "novo_colaborador",
            "senha": "SenhaNova123",
        },
    )

    # Verifica se o cadastro redirecionou para o login.
    assert resposta.status_code == 302
    assert resposta.url == reverse("login_colaborador")

    # Verifica se o usuário foi salvo no banco.
    usuario = Usuarios.objects.get(
        username="novo_colaborador"
    )

    assert usuario.nome_completo == "Novo Colaborador"
    assert usuario.email == "novo@exemplo.com"
    assert usuario.perfil_de_acesso == "colaborador"

    # Verifica se a senha foi armazenada criptografada.
    assert check_password("SenhaNova123", usuario.senha)


@pytest.mark.django_db
def test_cadastro_com_email_ja_existente(
    client,
    colaborador_existente,
):
    resposta = client.post(
        reverse("cadastro_colaborador"),
        {
            "nome_completo": "Outro Colaborador",
            "email": "existente@exemplo.com",
            "username": "outro_colaborador",
            "senha": "SenhaNova123",
        },
    )

    assert resposta.status_code == 200

    formulario = resposta.context["form"]

    assert "email" in formulario.errors
    assert Usuarios.objects.count() == 1


@pytest.mark.django_db
def test_cadastro_com_usuario_ja_existente(
    client,
    colaborador_existente,
):
    resposta = client.post(
        reverse("cadastro_colaborador"),
        {
            "nome_completo": "Outro Colaborador",
            "email": "outro@exemplo.com",
            "username": "colaborador_existente",
            "senha": "SenhaNova123",
        },
    )

    assert resposta.status_code == 200

    formulario = resposta.context["form"]

    assert "username" in formulario.errors
    assert Usuarios.objects.count() == 1


@pytest.mark.django_db
def test_cadastro_com_campos_vazios(client):
    resposta = client.post(
        reverse("cadastro_colaborador"),
        {
            "nome_completo": "",
            "email": "",
            "username": "",
            "senha": "",
        },
    )

    assert resposta.status_code == 200

    formulario = resposta.context["form"]

    assert formulario.errors
    assert Usuarios.objects.count() == 0