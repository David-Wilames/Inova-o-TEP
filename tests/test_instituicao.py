import json
from unittest.mock import patch

import pytest
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.test import RequestFactory

from instituicao.views import (
    pagina_instituicao,
    perfil_colaborador_api,
)
from usuario.models import InformacoesColaborador, Usuarios


@pytest.fixture
def criar_perfil_colaborador(db):
    def criar(username, nome, ativo=True):

        usuario = Usuarios.objects.create(
            nome_completo=nome,
            email=f"{username}@exemplo.com",
            username=username,
            senha=make_password("SenhaTeste123"),
            perfil_de_acesso="colaborador",
        )

        informacoes = InformacoesColaborador.objects.create(
            usuario=usuario,
            nome_completo=nome,
            nome_social="",
            materia="Matemática",
            municipio="Cajamar",
            uf="SP",
            perfil_ativo=ativo,
        )

        return informacoes

    return criar


def test_instituicao_lista_apenas_perfis_ativos(
    criar_perfil_colaborador,
):
    ativo = criar_perfil_colaborador(
        "professor_ativo",
        "Professor Ativo",
        True,
    )

    desativado = criar_perfil_colaborador(
        "professor_desativado",
        "Professor Desativado",
        False,
    )

    request = RequestFactory().get("/instituicao/")

    # Captura o contexto enviado pela view ao HTML.
    with patch(
        "instituicao.views.render",
        return_value=HttpResponse("OK"),
    ) as render_mock:
        resposta = pagina_instituicao(request)

    contexto = render_mock.call_args.args[2]

    colaboradores = list(contexto["colaboradores"])

    assert resposta.status_code == 200

    assert len(colaboradores) == 1

    assert colaboradores[0].pk == ativo.pk

    assert desativado.pk not in [colaborador.pk for colaborador in colaboradores]


def test_api_retorna_perfil_ativo(
    criar_perfil_colaborador,
):
    colaborador = criar_perfil_colaborador(
        "professor_api",
        "Professor API",
        True,
    )

    request = RequestFactory().get("/")

    resposta = perfil_colaborador_api(
        request,
        colaborador.pk,
    )

    dados = json.loads(resposta.content)

    assert resposta.status_code == 200

    assert dados["sucesso"] is True

    assert dados["colaborador"]["nome_completo"] == "Professor API"

    assert dados["colaborador"]["materia"] == "Matemática"


def test_api_bloqueia_perfil_desativado(
    criar_perfil_colaborador,
):
    colaborador = criar_perfil_colaborador(
        "professor_oculto",
        "Professor Oculto",
        False,
    )

    request = RequestFactory().get("/")

    resposta = perfil_colaborador_api(
        request,
        colaborador.pk,
    )

    dados = json.loads(resposta.content)

    assert resposta.status_code == 404

    assert dados["sucesso"] is False

    assert dados["mensagem"] == "Colaborador não encontrado."


@pytest.mark.django_db
def test_api_bloqueia_colaborador_inexistente():
    request = RequestFactory().get("/")

    resposta = perfil_colaborador_api(
        request,
        999999,
    )

    dados = json.loads(resposta.content)

    assert resposta.status_code == 404

    assert dados["sucesso"] is False


def test_api_perfil_aceita_somente_get(
    criar_perfil_colaborador,
):
    colaborador = criar_perfil_colaborador(
        "professor_metodo",
        "Professor Método",
        True,
    )

    request = RequestFactory().post("/")

    resposta = perfil_colaborador_api(
        request,
        colaborador.pk,
    )

    assert resposta.status_code == 405
