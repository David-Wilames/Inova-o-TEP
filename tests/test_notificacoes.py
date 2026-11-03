from datetime import timedelta

import pytest
from django.db import connection
from django.urls import reverse
from django.utils import timezone

from instituicao.models import Escolas, InteresseOportunidade
from usuario.models import InformacoesColaborador, Usuarios

# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture
def usuario_teste(db):
    return Usuarios.objects.create(
        nome_completo="Colaborador Teste",
        email="colaborador@exemplo.com",
        username="colaborador_teste",
        senha="senha_criptografada_teste",
        perfil_de_acesso="colaborador",
    )


@pytest.fixture
def colaborador_teste(usuario_teste):
    return InformacoesColaborador.objects.create(
        usuario=usuario_teste,
        nome_completo="Colaborador Teste",
        nome_social="",
        materia="Matemática",
    )


@pytest.fixture
def cliente_colaborador(client, colaborador_teste):
    session = client.session

    session["usuario_id"] = colaborador_teste.usuario_id

    session.save()

    return client


@pytest.fixture
def escola_teste(db):
    return Escolas.objects.create(
        nome_unidade_escolar="Escola Teste",
        telefone="11999999999",
        endereco="Rua de Teste",
        municipio="Cajamar",
        bairro_localidade="Centro",
        cep="07750-000",
        diretor="Diretor Teste",
        categoria="Municipal",
    )


@pytest.fixture
def outra_escola(db):
    return Escolas.objects.create(
        nome_unidade_escolar="Outra Escola",
        telefone="11888888888",
        endereco="Rua Secundária",
        municipio="Cajamar",
        bairro_localidade="Centro",
        cep="07750-001",
        diretor="Outro Diretor",
        categoria="Estadual",
    )


# =====================================================
# TABELA DE OPORTUNIDADES PARA OS TESTES
# =====================================================

@pytest.fixture
def tabela_oportunidades(db):

    # A tabela informacoes_instituicao utiliza managed=False.
    # Por isso, ela precisa ser criada manualmente
    # no banco temporário de testes.

    with connection.cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS "informacoes_instituicao"
        """)

        cursor.execute("""
            CREATE TABLE "informacoes_instituicao" (
                "Escola" TEXT NOT NULL,
                "Materia" TEXT,
                "Tipo" TEXT
            )
        """)

    yield

    with connection.cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS "informacoes_instituicao"
        """)


def inserir_oportunidade(nome_escola):
    with connection.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO "informacoes_instituicao" (
                "Escola",
                "Materia",
                "Tipo"
            )
            VALUES (%s, %s, %s)
            """,
            [
                nome_escola,
                "Matemática",
                "aula",
            ],
        )

        return cursor.lastrowid


@pytest.fixture
def oportunidade_teste(tabela_oportunidades, escola_teste):
    return inserir_oportunidade(
        escola_teste.nome_unidade_escolar
    )


# =====================================================
# REGISTRO DE INTERESSE
# =====================================================

@pytest.mark.django_db
def test_registrar_interesse_exige_login(client):

    resposta = client.post(
        reverse("registrar_interesse"),
        {
            "oportunidade_id": "1",
        },
    )

    assert resposta.status_code == 401

    assert resposta.json()["sucesso"] is False


@pytest.mark.django_db
def test_registrar_interesse_com_id_invalido(
    cliente_colaborador,
):

    resposta = cliente_colaborador.post(
        reverse("registrar_interesse"),
        {
            "oportunidade_id": "abc",
        },
    )

    assert resposta.status_code == 400

    assert resposta.json()["sucesso"] is False


@pytest.mark.django_db
def test_registrar_interesse_com_oportunidade_inexistente(
    cliente_colaborador,
    tabela_oportunidades,
):

    resposta = cliente_colaborador.post(
        reverse("registrar_interesse"),
        {
            "oportunidade_id": "999999",
        },
    )

    assert resposta.status_code == 404

    assert resposta.json()["sucesso"] is False


@pytest.mark.django_db
def test_registrar_interesse_com_instituicao_nao_encontrada(
    cliente_colaborador,
    tabela_oportunidades,
):

    oportunidade_id = inserir_oportunidade(
        "Escola Inexistente"
    )

    resposta = cliente_colaborador.post(
        reverse("registrar_interesse"),
        {
            "oportunidade_id": oportunidade_id,
        },
    )

    assert resposta.status_code == 404

    assert resposta.json()["sucesso"] is False


@pytest.mark.django_db
def test_registrar_interesse_sem_perfil_cadastrado(
    client,
    usuario_teste,
    escola_teste,
    oportunidade_teste,
):

    session = client.session

    session["usuario_id"] = usuario_teste.pk

    session.save()

    resposta = client.post(
        reverse("registrar_interesse"),
        {
            "oportunidade_id": oportunidade_teste,
        },
    )

    assert resposta.status_code == 400

    assert resposta.json()["sucesso"] is False

    assert InteresseOportunidade.objects.count() == 0


@pytest.mark.django_db
def test_registrar_interesse_com_sucesso(
    cliente_colaborador,
    colaborador_teste,
    escola_teste,
    oportunidade_teste,
):

    resposta = cliente_colaborador.post(
        reverse("registrar_interesse"),
        {
            "oportunidade_id": oportunidade_teste,
        },
    )

    dados = resposta.json()

    assert resposta.status_code == 201

    assert dados["sucesso"] is True

    notificacao = InteresseOportunidade.objects.get(
        pk=dados["notificacao_id"]
    )

    assert notificacao.escola_id == escola_teste.pk

    assert notificacao.colaborador_id == colaborador_teste.pk

    assert notificacao.oportunidade_id == oportunidade_teste

    assert notificacao.materia == "Matemática"

    assert notificacao.tipo == "aula"

    duracao = notificacao.expira_em - notificacao.criado_em

    assert timedelta(hours=9, minutes=59) <= duracao <= timedelta(hours=10)


@pytest.mark.django_db
def test_registrar_interesse_nao_duplica_notificacao(
    cliente_colaborador,
    escola_teste,
    oportunidade_teste,
):

    primeira_resposta = cliente_colaborador.post(
        reverse("registrar_interesse"),
        {
            "oportunidade_id": oportunidade_teste,
        },
    )

    segunda_resposta = cliente_colaborador.post(
        reverse("registrar_interesse"),
        {
            "oportunidade_id": oportunidade_teste,
        },
    )

    assert primeira_resposta.status_code == 201

    assert segunda_resposta.status_code == 200

    assert segunda_resposta.json()["sucesso"] is True

    assert InteresseOportunidade.objects.count() == 1


# =====================================================
# CONSULTA DAS NOTIFICAÇÕES PELA INSTITUIÇÃO
# =====================================================

@pytest.mark.django_db
def test_listar_notificacoes_exige_instituicao_autenticada(client):

    resposta = client.get(
        reverse("listar_notificacoes_interesse")
    )

    assert resposta.status_code == 403

    assert resposta.json()["sucesso"] is False


@pytest.mark.django_db
def test_listar_notificacoes_com_instituicao_inexistente(client):

    session = client.session

    session["escola_autenticada_id"] = 999999

    session.save()

    resposta = client.get(
        reverse("listar_notificacoes_interesse")
    )

    assert resposta.status_code == 403

    assert resposta.json()["sucesso"] is False

    assert "escola_autenticada_id" not in client.session


@pytest.mark.django_db
def test_listar_notificacoes_mostra_somente_da_escola(
    client,
    colaborador_teste,
    escola_teste,
    outra_escola,
):

    agora = timezone.now()

    # Notificação válida da instituição selecionada.
    notificacao_escola = InteresseOportunidade.objects.create(
        escola=escola_teste,
        colaborador=colaborador_teste,
        oportunidade_id=1,
        materia="Matemática",
        tipo="aula",
        expira_em=agora + timedelta(hours=5),
    )

    # Notificação válida de outra instituição.
    notificacao_outra_escola = InteresseOportunidade.objects.create(
        escola=outra_escola,
        colaborador=colaborador_teste,
        oportunidade_id=2,
        materia="História",
        tipo="horas",
        expira_em=agora + timedelta(hours=5),
    )

    # Notificação expirada.
    notificacao_expirada = InteresseOportunidade.objects.create(
        escola=escola_teste,
        colaborador=colaborador_teste,
        oportunidade_id=3,
        materia="Português",
        tipo="aula",
        expira_em=agora - timedelta(hours=1),
    )

    session = client.session

    session["escola_autenticada_id"] = escola_teste.pk

    session.save()

    resposta = client.get(
        reverse("listar_notificacoes_interesse")
    )

    dados = resposta.json()

    assert resposta.status_code == 200

    assert dados["sucesso"] is True

    assert dados["instituicao"] == "Escola Teste"

    assert dados["total"] == 1

    assert len(dados["notificacoes"]) == 1

    assert dados["notificacoes"][0]["nome_colaborador"] == "Colaborador Teste"

    assert dados["notificacoes"][0]["materia"] == "Matemática"

    assert dados["notificacoes"][0]["tipo"] == "aula"

    # A notificação da outra escola não foi exibida.
    assert InteresseOportunidade.objects.filter(
        pk=notificacao_outra_escola.pk
    ).exists()

    # A notificação expirada foi removida.
    assert not InteresseOportunidade.objects.filter(
        pk=notificacao_expirada.pk
    ).exists()

    # A notificação válida continua armazenada.
    assert InteresseOportunidade.objects.filter(
        pk=notificacao_escola.pk
    ).exists()


# =====================================================
# VALIDAÇÃO DOS MÉTODOS HTTP
# =====================================================

@pytest.mark.django_db
def test_endpoints_aceitam_somente_os_metodos_permitidos(client):

    # Registrar interesse aceita somente POST.
    resposta_interesse = client.get(
        reverse("registrar_interesse")
    )

    assert resposta_interesse.status_code == 405

    # Listar notificações aceita somente GET.
    resposta_notificacoes = client.post(
        reverse("listar_notificacoes_interesse")
    )

    assert resposta_notificacoes.status_code == 405