from datetime import date

import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from usuario.models import InformacoesColaborador, Usuarios


@pytest.fixture
def colaborador_teste(db):
    return Usuarios.objects.create(
        nome_completo="Colaborador Teste",
        email="colaborador.teste@exemplo.com",
        username="colaborador_teste",
        senha=make_password("SenhaTeste123"),
        perfil_de_acesso="colaborador",
    )


@pytest.fixture
def cliente_autenticado(client, colaborador_teste):
    session = client.session
    session["usuario_id"] = colaborador_teste.pk
    session.save()

    return client


@pytest.mark.django_db
def test_adicionar_informacoes_exige_login(client):
    resposta = client.get(reverse("adicionar_informacoes"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("login_colaborador")


@pytest.mark.django_db
def test_informacoes_colaborador_exige_login(client):
    resposta = client.get(reverse("informacoes_colaborador"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("login_colaborador")


@pytest.mark.django_db
def test_adicionar_informacoes_cria_perfil_vazio(
    cliente_autenticado,
    colaborador_teste,
):
    resposta = cliente_autenticado.get(reverse("adicionar_informacoes"))

    assert resposta.status_code == 200

    informacoes = InformacoesColaborador.objects.get(usuario=colaborador_teste)

    assert informacoes.usuario_id == colaborador_teste.pk


@pytest.mark.django_db
def test_salvar_informacoes_do_colaborador(
    cliente_autenticado,
    colaborador_teste,
):
    dados = {
        "nome_completo": "Colaborador Teste",
        "nome_social": "Nome Social",
        "data_nascimento": "1995-05-20",
        "genero": "Masculino",
        "possui_deficiencia": "nao",
        "necessidades_acessibilidade": "",
        "email": "colaborador.teste@exemplo.com",
        "telefone": "11999999999",
        "cep": "07750-000",
        "numero": "100",
        "logradouro": "Rua de Teste",
        "complemento": "Casa",
        "bairro": "Centro",
        "municipio": "Cajamar",
        "uf": "SP",
        "tipo_documento": "RG",
        "rg": "123456789",
        "cpf": "12345678901",
        "materia": "Matemática",
        "tempo_integral": "sim",
        "horario_inicio": "08:00",
        "horario_fim": "17:00",
        "formacao": "Licenciatura",
        "pos_graduacao": "Especialização",
        "disciplinas": ["Matemática", "Português"],
        "observacoes": "Informações de teste.",
    }

    resposta = cliente_autenticado.post(
        reverse("adicionar_informacoes"),
        data=dados,
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse("colaborador")

    informacoes = InformacoesColaborador.objects.get(usuario=colaborador_teste)

    assert informacoes.nome_completo == "Colaborador Teste"
    assert informacoes.nome_social == "Nome Social"
    assert informacoes.data_nascimento == date(1995, 5, 20)
    assert informacoes.municipio == "Cajamar"
    assert informacoes.uf == "SP"
    assert informacoes.materia == "Matemática"
    assert informacoes.tempo_integral is True
    assert informacoes.horario_inicio.strftime("%H:%M") == "08:00"
    assert informacoes.horario_fim.strftime("%H:%M") == "17:00"
    assert informacoes.disciplinas == ["Matemática", "Português"]


@pytest.mark.django_db
def test_visualizar_informacoes_salvas(
    cliente_autenticado,
    colaborador_teste,
):
    InformacoesColaborador.objects.create(
        usuario=colaborador_teste,
        nome_completo="Colaborador Teste",
        materia="História",
        municipio="Cajamar",
        uf="SP",
    )

    resposta = cliente_autenticado.get(reverse("informacoes_colaborador"))

    assert resposta.status_code == 200

    assert resposta.context["usuario"].pk == colaborador_teste.pk

    informacoes = resposta.context["informacoes"]

    assert informacoes is not None
    assert informacoes.materia == "História"
    assert informacoes.municipio == "Cajamar"


@pytest.mark.django_db
def test_sessao_com_usuario_inexistente(
    client,
):
    session = client.session
    session["usuario_id"] = 999999
    session.save()

    resposta = client.get(reverse("informacoes_colaborador"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("login_colaborador")
    assert "usuario_id" not in client.session


@pytest.mark.django_db
def test_desativar_perfil_do_colaborador(
    cliente_autenticado,
    colaborador_teste,
):
    informacoes = InformacoesColaborador.objects.create(
        usuario=colaborador_teste,
        perfil_ativo=True,
    )

    resposta = cliente_autenticado.post(reverse("alternar_visibilidade_perfil"))

    informacoes.refresh_from_db()

    assert resposta.status_code == 302
    assert resposta.url == reverse("informacoes_colaborador")
    assert informacoes.perfil_ativo is False


@pytest.mark.django_db
def test_ativar_perfil_do_colaborador(
    cliente_autenticado,
    colaborador_teste,
):
    informacoes = InformacoesColaborador.objects.create(
        usuario=colaborador_teste,
        perfil_ativo=False,
    )

    resposta = cliente_autenticado.post(reverse("alternar_visibilidade_perfil"))

    informacoes.refresh_from_db()

    assert resposta.status_code == 302
    assert resposta.url == reverse("informacoes_colaborador")
    assert informacoes.perfil_ativo is True


@pytest.mark.django_db
def test_alterar_visibilidade_exige_login(client):
    resposta = client.post(reverse("alternar_visibilidade_perfil"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("login_colaborador")


@pytest.mark.django_db
def test_alterar_visibilidade_sem_perfil(
    cliente_autenticado,
):
    resposta = cliente_autenticado.post(reverse("alternar_visibilidade_perfil"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("adicionar_informacoes")
