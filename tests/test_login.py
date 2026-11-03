import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from usuario.models import Usuarios


@pytest.fixture
def colaborador_teste(db):
    return Usuarios.objects.create(
        nome_completo="Colaborador Teste",
        email="colaborador.teste@exemplo.com",
        username="colaborador_teste",
        senha=make_password("SenhaTeste123"),
        perfil_de_acesso="colaborador",
    )


@pytest.mark.django_db
def test_login_com_usuario_e_senha_corretos(
    client,
    colaborador_teste,
):
    resposta = client.post(
        reverse("login_colaborador"),
        {
            "usuario": "colaborador_teste",
            "senha": "SenhaTeste123",
        },
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse("colaborador")


@pytest.mark.django_db
def test_login_com_email_e_senha_corretos(
    client,
    colaborador_teste,
):
    resposta = client.post(
        reverse("login_colaborador"),
        {
            "usuario": "colaborador.teste@exemplo.com",
            "senha": "SenhaTeste123",
        },
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse("colaborador")


@pytest.mark.django_db
def test_login_com_senha_incorreta(
    client,
    colaborador_teste,
):
    resposta = client.post(
        reverse("login_colaborador"),
        {
            "usuario": "colaborador_teste",
            "senha": "SenhaErrada123",
        },
    )

    assert resposta.status_code == 200
    assert "Senha incorreta." in resposta.content.decode()


@pytest.mark.django_db
def test_login_com_usuario_inexistente(client):
    resposta = client.post(
        reverse("login_colaborador"),
        {
            "usuario": "usuario_inexistente",
            "senha": "SenhaTeste123",
        },
    )

    assert resposta.status_code == 200
    assert "Usuário ou e-mail não encontrado." in (
        resposta.content.decode()
    )


@pytest.mark.django_db
def test_login_com_campos_vazios(client):
    resposta = client.post(
        reverse("login_colaborador"),
        {
            "usuario": "",
            "senha": "",
        },
    )

    assert resposta.status_code == 200