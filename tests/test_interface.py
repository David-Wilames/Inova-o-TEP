import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from datetime import timedelta

import pytest
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import expect

from usuario.models import InformacoesColaborador, Usuarios


@pytest.fixture
def colaborador_ui():
    return Usuarios.objects.create(
        nome_completo="Colaborador Playwright",
        email="playwright@exemplo.com",
        username="colaborador_playwright",
        senha=make_password("SenhaTeste123"),
        perfil_de_acesso="colaborador",
    )


@pytest.mark.django_db(transaction=True)
def test_pagina_login_abre_no_navegador(page, live_server):

    resposta = page.goto(
        f"{live_server.url}{reverse('login_colaborador')}",
        wait_until="domcontentloaded",
    )

    assert resposta is not None
    assert resposta.status == 200

    expect(
        page.get_by_role("heading", name="Entrar como professor")
    ).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_login_visual_com_credenciais_corretas(
    page,
    live_server,
    colaborador_ui,
):

    page.goto(
        f"{live_server.url}{reverse('login_colaborador')}",
        wait_until="domcontentloaded",
    )

    page.locator('input[name="usuario"]').fill(
        "colaborador_playwright"
    )

    page.locator('input[name="senha"]').fill(
        "SenhaTeste123"
    )

    with page.expect_navigation(wait_until="domcontentloaded"):
        page.get_by_role("button", name="Entrar").click()

    expect(page).to_have_url(
        f"{live_server.url}{reverse('colaborador')}"
    )


@pytest.mark.django_db(transaction=True)
def test_login_visual_com_senha_incorreta(
    page,
    live_server,
    colaborador_ui,
):

    page.goto(
        f"{live_server.url}{reverse('login_colaborador')}",
        wait_until="domcontentloaded",
    )

    page.locator('input[name="usuario"]').fill(
        "colaborador_playwright"
    )

    page.locator('input[name="senha"]').fill(
        "SenhaErrada123"
    )

    page.get_by_role("button", name="Entrar").click()

    expect(
        page.get_by_text("Senha incorreta.", exact=True)
    ).to_be_visible()

    expect(page).to_have_url(
        f"{live_server.url}{reverse('login_colaborador')}"
    )


@pytest.fixture
def colaborador_existente_ui(db):
    return Usuarios.objects.create(
        nome_completo="Colaborador Existente",
        email="existente@exemplo.com",
        username="colaborador_existente",
        senha=make_password("SenhaTeste123"),
        perfil_de_acesso="colaborador",
    )


@pytest.mark.django_db(transaction=True)
def test_pagina_cadastro_abre_no_navegador(page, live_server):

    resposta = page.goto(
        f"{live_server.url}{reverse('cadastro_colaborador')}",
        wait_until="domcontentloaded",
    )

    assert resposta is not None
    assert resposta.status == 200

    expect(
        page.get_by_role("heading", name="Cadastro de professor")
    ).to_be_visible()

    expect(
        page.get_by_role("button", name="Criar conta")
    ).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_cadastro_visual_com_dados_validos(page, live_server):

    page.goto(
        f"{live_server.url}{reverse('cadastro_colaborador')}",
        wait_until="domcontentloaded",
    )

    page.locator('input[name="nome_completo"]').fill(
        "Colaborador Playwright"
    )

    page.locator('input[name="email"]').fill(
        "playwright.cadastro@exemplo.com"
    )

    page.locator('input[name="username"]').fill(
        "playwright_cadastro"
    )

    page.locator('input[name="senha"]').fill(
        "SenhaPlaywright123"
    )

    with page.expect_navigation(wait_until="domcontentloaded"):
        page.get_by_role("button", name="Criar conta").click()

    expect(page).to_have_url(
        f"{live_server.url}{reverse('login_colaborador')}"
    )

    usuario = Usuarios.objects.get(
        username="playwright_cadastro"
    )

    assert usuario.nome_completo == "Colaborador Playwright"
    assert usuario.email == "playwright.cadastro@exemplo.com"

    from django.contrib.auth.hashers import check_password

    assert check_password("SenhaPlaywright123", usuario.senha)


@pytest.mark.django_db(transaction=True)
def test_cadastro_visual_com_email_existente(
    page,
    live_server,
    colaborador_existente_ui,
):

    page.goto(
        f"{live_server.url}{reverse('cadastro_colaborador')}",
        wait_until="domcontentloaded",
    )

    page.locator('input[name="nome_completo"]').fill(
        "Outro Colaborador"
    )

    page.locator('input[name="email"]').fill(
        "existente@exemplo.com"
    )

    page.locator('input[name="username"]').fill(
        "outro_colaborador"
    )

    page.locator('input[name="senha"]').fill(
        "SenhaNova123"
    )

    page.get_by_role("button", name="Criar conta").click()

    expect(
        page.get_by_text(
            "Já existe uma conta cadastrada com este e-mail.",
            exact=True,
        )
    ).to_be_visible()

    expect(page).to_have_url(
        f"{live_server.url}{reverse('cadastro_colaborador')}"
    )

# =====================================================
# AUXILIAR PARA LOGIN NO NAVEGADOR
# =====================================================

def fazer_login_no_navegador(page, live_server):

    page.goto(
        f"{live_server.url}{reverse('login_colaborador')}",
        wait_until="domcontentloaded",
    )

    page.locator('input[name="usuario"]').fill(
        "colaborador_playwright"
    )

    page.locator('input[name="senha"]').fill(
        "SenhaTeste123"
    )

    with page.expect_navigation(wait_until="domcontentloaded"):
        page.get_by_role("button", name="Entrar").click()


# =====================================================
# TESTE 1 - ACESSO AO FORMULÁRIO SEM LOGIN
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_adicionar_informacoes_exige_login_no_navegador(
    page,
    live_server,
):

    page.goto(
        f"{live_server.url}{reverse('adicionar_informacoes')}",
        wait_until="domcontentloaded",
    )

    expect(page).to_have_url(
        f"{live_server.url}{reverse('login_colaborador')}"
    )


# =====================================================
# TESTE 2 - SALVAR INFORMAÇÕES PELO NAVEGADOR
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_salvar_informacoes_pelo_navegador(
    page,
    live_server,
    colaborador_ui,
):

    fazer_login_no_navegador(page, live_server)

    page.goto(
        f"{live_server.url}{reverse('adicionar_informacoes')}",
        wait_until="domcontentloaded",
    )

    expect(
        page.get_by_role("heading", name="Adicionar informações")
    ).to_be_visible()

    # Dados pessoais
    page.locator("#nome_completo").fill(
        "Colaborador Playwright"
    )

    page.locator("#informar_nome_social").check()

    page.locator("#nome_social").fill(
        "Nome Social Teste"
    )

    page.locator("#data_nascimento").fill(
        "1995-05-20"
    )

    page.locator("#genero").select_option("masculino")

    page.locator("#possui_deficiencia").select_option("nao")

    # Contato
    page.locator("#email").fill(
        "playwright@exemplo.com"
    )

    page.locator("#telefone").fill(
        "11999999999"
    )

    # Endereço
    page.locator("#cep").fill(
        "07750000"
    )

    page.locator("#numero").fill("100")

    page.locator("#logradouro").fill(
        "Rua de Teste"
    )

    page.locator("#bairro").fill(
        "Centro"
    )

    page.locator("#municipio").fill(
        "Cajamar"
    )

    page.locator("#uf").select_option("SP")

    # Área profissional
    page.locator("#materia").fill(
        "Matemática"
    )

    # Disponibilidade
    page.locator("#inicio").fill("08:00")

    page.locator("#fim").fill("17:00")

    # Formação
    page.locator("#formacao").fill(
        "Licenciatura em Matemática"
    )

    page.locator("#pos_graduacao").fill(
        "Educação Matemática"
    )

    # Disciplinas
    page.locator(
        'input[name="disciplinas"][value="matematica"]'
    ).check()

    page.locator(
        'input[name="disciplinas"][value="portugues"]'
    ).check()

    # Observações
    page.locator("#observacoes").fill(
        "Teste automatizado com Playwright."
    )

    # Salvar formulário
    with page.expect_navigation(wait_until="domcontentloaded"):
        page.get_by_role(
            "button",
            name="Salvar informações",
        ).click()

    expect(page).to_have_url(
        f"{live_server.url}{reverse('colaborador')}"
    )

    # Confere os dados diretamente no banco de testes.
    informacoes = InformacoesColaborador.objects.get(
        usuario=colaborador_ui
    )

    assert informacoes.nome_completo == "Colaborador Playwright"

    assert informacoes.nome_social == "Nome Social Teste"

    assert informacoes.cep == "07750-000"

    assert informacoes.municipio == "Cajamar"

    assert informacoes.uf == "SP"

    assert informacoes.materia == "Matemática"

    assert informacoes.horario_inicio.strftime("%H:%M") == "08:00"

    assert informacoes.horario_fim.strftime("%H:%M") == "17:00"

    assert informacoes.disciplinas == [
        "matematica",
        "portugues",
    ]


# =====================================================
# TESTE 3 - VISUALIZAR CURRÍCULO NO NAVEGADOR
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_visualizar_curriculo_pelo_navegador(
    page,
    live_server,
    colaborador_ui,
):

    InformacoesColaborador.objects.create(
        usuario=colaborador_ui,
        nome_completo="Colaborador Playwright",
        nome_social="Nome Social Teste",
        materia="História",
        municipio="Cajamar",
        uf="SP",
        formacao="Licenciatura",
        perfil_ativo=True,
    )

    fazer_login_no_navegador(page, live_server)

    page.goto(
        f"{live_server.url}{reverse('informacoes_colaborador')}",
        wait_until="domcontentloaded",
    )

    expect(
        page.get_by_role(
            "heading",
            name="Colaborador Playwright",
        )
    ).to_be_visible()

    expect(
        page.get_by_text("Nome Social: Nome Social Teste")
    ).to_be_visible()

    expect(
        page.get_by_text("Seu perfil está ativado e visível para as instituições.")
    ).to_be_visible()


# =====================================================
# TESTE 4 - ATIVAR E DESATIVAR PERFIL NO NAVEGADOR
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_alternar_visibilidade_pelo_navegador(
    page,
    live_server,
    colaborador_ui,
):

    InformacoesColaborador.objects.create(
        usuario=colaborador_ui,
        nome_completo="Colaborador Playwright",
        materia="Matemática",
        perfil_ativo=True,
    )

    fazer_login_no_navegador(page, live_server)

    page.goto(
        f"{live_server.url}{reverse('informacoes_colaborador')}",
        wait_until="domcontentloaded",
    )

    # Confirma que o perfil começa ativado.
    expect(
        page.get_by_role("button", name="Desativar perfil")
    ).to_be_visible()

    # Desativa o perfil.
    with page.expect_navigation(wait_until="domcontentloaded"):
        page.get_by_role("button", name="Desativar perfil").click()

    expect(
        page.get_by_text("Seu perfil está desativado e oculto das instituições.")
    ).to_be_visible()

    expect(
        page.get_by_role("button", name="Ativar perfil")
    ).to_be_visible()

    informacoes = InformacoesColaborador.objects.get(
        usuario=colaborador_ui
    )

    informacoes.refresh_from_db()

    assert informacoes.perfil_ativo is False

    # Reativa o perfil.
    with page.expect_navigation(wait_until="domcontentloaded"):
        page.get_by_role("button", name="Ativar perfil").click()

    expect(
        page.get_by_text("Seu perfil está ativado e visível para as instituições.")
    ).to_be_visible()

    informacoes.refresh_from_db()

    assert informacoes.perfil_ativo is True

# =====================================================
# TESTES DE INTERFACE DA INSTITUIÇÃO
# =====================================================

@pytest.fixture
def escola_ui():
    from instituicao.models import Escolas

    return Escolas.objects.create(
        nome_unidade_escolar="Escola Playwright",
        telefone="11987654321",
        endereco="Rua de Teste, 100",
        municipio="Cajamar",
        bairro_localidade="Centro",
        cep="07750-000",
        diretor="Diretor Playwright",
        categoria="Municipal",
    )


@pytest.fixture
def perfil_colaborador_instituicao_ui(colaborador_ui):
    return InformacoesColaborador.objects.create(
        usuario=colaborador_ui,
        nome_completo="Colaborador Playwright",
        nome_social="Colaborador Social Playwright",
        genero="Masculino",
        email="playwright@exemplo.com",
        telefone="11999999999",
        municipio="Cajamar",
        uf="SP",
        cep="07750-000",
        logradouro="Rua de Teste",
        numero="100",
        bairro="Centro",
        materia="Matemática",
        formacao="Licenciatura em Matemática",
        perfil_ativo=True,
    )


@pytest.fixture
def tabela_informacoes_instituicao_ui(db):
    """
    Garante que a tabela existente de oportunidades esteja
    disponível no banco de testes.

    O modelo InformacoesInstituicao utiliza managed=False.
    Por isso, o Django não cria essa tabela automaticamente.
    """

    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "informacoes_instituicao" (
                "Escola" TEXT,
                "Telefone" TEXT,
                "CEP" TEXT,
                "Endereço" TEXT,
                "Municipio" TEXT,
                "Bairro" TEXT,
                "Materia" TEXT,
                "Tipo" TEXT,
                "Quantidade" TEXT,
                "Nome do responsavel" TEXT,
                "Observacoes" TEXT
            )
        """)


def abrir_selecao_instituicao(page, live_server, escola):
    """
    Abre o painel lateral e a janela de seleção de escolas.
    """

    page.goto(
        f"{live_server.url}{reverse('pagina_instituicao')}",
        wait_until="domcontentloaded",
    )

    # Abre o painel lateral.
    page.locator("#abrir-painel-notificacoes").click()

    expect(
        page.locator("#painel-notificacoes")
    ).to_have_attribute("aria-hidden", "false")

    # Abre a seleção de instituição.
    page.locator("#botao-instituicao").click()

    expect(
        page.locator("#modal-escolas")
    ).to_have_attribute("aria-hidden", "false")

    # Aguarda a escola ser carregada pela API.
    radio_escola = page.locator(
        f'#lista-escolas input[name="escola"][value="{escola.pk}"]'
    )

    expect(radio_escola).to_be_visible()


def selecionar_escola_no_navegador(page, escola):
    """
    Seleciona uma escola e abre o modal de senha.
    """

    opcao = page.locator(
        "#lista-escolas .escola-opcao"
    ).filter(has_text=escola.nome_unidade_escolar)

    opcao.click()

    radio = page.locator(
        f'#lista-escolas input[name="escola"][value="{escola.pk}"]'
    )

    expect(radio).to_be_checked()

    page.locator("#confirmar-escola").click()

    expect(
        page.locator("#modal-senha-instituicao")
    ).to_have_attribute("aria-hidden", "false")


# =====================================================
# TESTE 1 - LISTAR SOMENTE COLABORADORES ATIVOS
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_instituicao_lista_apenas_perfis_ativos(
    page,
    live_server,
    perfil_colaborador_instituicao_ui,
):

    from django.contrib.auth.hashers import make_password

    # Cria um segundo usuário com perfil desativado.
    usuario_inativo = Usuarios.objects.create(
        nome_completo="Colaborador Inativo",
        email="inativo@exemplo.com",
        username="colaborador_inativo_ui",
        senha=make_password("SenhaTeste123"),
        perfil_de_acesso="colaborador",
    )

    InformacoesColaborador.objects.create(
        usuario=usuario_inativo,
        nome_completo="Colaborador Inativo",
        materia="História",
        perfil_ativo=False,
    )

    page.goto(
        f"{live_server.url}{reverse('pagina_instituicao')}",
        wait_until="domcontentloaded",
    )

    # O perfil ativo deve aparecer.
    expect(
        page.get_by_text(
            "Colaborador Social Playwright",
            exact=True,
        )
    ).to_be_visible()

    # O perfil desativado não deve aparecer.
    expect(
        page.get_by_text(
            "Colaborador Inativo",
            exact=True,
        )
    ).to_have_count(0)

    # Somente um colaborador deve estar listado.
    expect(
        page.locator(".teacher-card")
    ).to_have_count(1)


# =====================================================
# TESTE 2 - ABRIR O PERFIL DO COLABORADOR
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_modal_exibe_perfil_do_colaborador(
    page,
    live_server,
    perfil_colaborador_instituicao_ui,
):

    perfil = perfil_colaborador_instituicao_ui

    page.goto(
        f"{live_server.url}{reverse('pagina_instituicao')}",
        wait_until="domcontentloaded",
    )

    botao_perfil = page.locator(
        f'.profile-btn[data-colaborador-id="{perfil.pk}"]'
    )

    expect(botao_perfil).to_be_visible()

    # Aguarda a consulta à API do perfil.
    with page.expect_response(
        lambda resposta: (
            "/instituicao/api/colaborador/" in resposta.url
            and "/perfil/" in resposta.url
        )
    ) as resposta_api:

        botao_perfil.click()

    resposta = resposta_api.value

    assert resposta.status == 200

    # Confere a abertura do modal.
    expect(
        page.locator("#perfil-modal")
    ).to_have_attribute("aria-hidden", "false")

    # Confere as informações carregadas.
    expect(
        page.locator("#perfil-conteudo")
    ).to_be_visible()

    expect(
        page.locator('[data-campo="materia"]')
    ).to_have_text("Matemática")


# =====================================================
# TESTE 3 - ABRIR PAINEL E CARREGAR ESCOLAS
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_painel_instituicao_carrega_lista_de_escolas(
    page,
    live_server,
    escola_ui,
):

    abrir_selecao_instituicao(
        page,
        live_server,
        escola_ui,
    )

    # Confirma que a escola aparece na lista.
    expect(
        page.locator("#lista-escolas")
    ).to_contain_text("Escola Playwright")

    # Confirma que existe uma opção de escola.
    expect(
        page.locator("#lista-escolas .escola-opcao")
    ).to_have_count(1)

    # O botão só deve ser habilitado depois da seleção.
    expect(
        page.locator("#confirmar-escola")
    ).to_be_disabled()

    page.locator(
        f'#lista-escolas input[name="escola"][value="{escola_ui.pk}"]'
    ).check()

    expect(
        page.locator("#confirmar-escola")
    ).to_be_enabled()


# =====================================================
# TESTE 4 - SELECIONAR ESCOLA E ABRIR MODAL DE SENHA
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_selecionar_escola_abre_modal_de_senha(
    page,
    live_server,
    escola_ui,
):

    abrir_selecao_instituicao(
        page,
        live_server,
        escola_ui,
    )

    selecionar_escola_no_navegador(
        page,
        escola_ui,
    )

    expect(
        page.locator("#nome-escola-senha")
    ).to_contain_text("Escola Playwright")

    expect(
        page.locator("#senha-instituicao")
    ).to_be_visible()


# =====================================================
# TESTE 5 - IMPEDIR ACESSO COM SENHA INCORRETA
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_instituicao_bloqueia_senha_incorreta_no_navegador(
    page,
    live_server,
    escola_ui,
    tabela_informacoes_instituicao_ui,
):

    abrir_selecao_instituicao(
        page,
        live_server,
        escola_ui,
    )

    selecionar_escola_no_navegador(
        page,
        escola_ui,
    )

    page.locator("#senha-instituicao").fill(
        "SenhaErrada123"
    )

    with page.expect_response(
        lambda resposta: (
            "/instituicao/verificar-instituicao/"
            in resposta.url
        )
    ) as resposta_api:

        page.locator(
            "#confirmar-senha-instituicao"
        ).click()

    resposta = resposta_api.value

    assert resposta.status == 403

    expect(
        page.locator("#mensagem-senha-instituicao")
    ).to_contain_text("Senha incorreta")

    # A área de notificações deve continuar bloqueada.
    assert page.locator(
        "#secao-notificacoes-interesse"
    ).evaluate("(elemento) => elemento.hidden") is True


# =====================================================
# TESTE 6 - CONFIRMAR INSTITUIÇÃO COM SENHA CORRETA
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_instituicao_confirma_acesso_com_senha_correta(
    page,
    live_server,
    escola_ui,
    tabela_informacoes_instituicao_ui,
):

    abrir_selecao_instituicao(
        page,
        live_server,
        escola_ui,
    )

    selecionar_escola_no_navegador(
        page,
        escola_ui,
    )

    # A senha corresponde ao telefone cadastrado.
    page.locator("#senha-instituicao").fill(
        escola_ui.telefone
    )

    with page.expect_response(
        lambda resposta: (
            "/instituicao/verificar-instituicao/"
            in resposta.url
        )
    ) as resposta_api:

        page.locator(
            "#confirmar-senha-instituicao"
        ).click()

    resposta = resposta_api.value

    assert resposta.status == 200

    dados = resposta.json()

    assert dados["sucesso"] is True
    assert dados["nome_escola"] == "Escola Playwright"

    # O modal de senha deve fechar.
    expect(
        page.locator("#modal-senha-instituicao")
    ).to_have_attribute("aria-hidden", "true")

    # A seção de notificações deve ser liberada.
    assert page.locator(
        "#secao-notificacoes-interesse"
    ).evaluate("(elemento) => elemento.hidden") is False

    expect(
        page.locator("#mensagem-senha-instituicao")
    ).to_contain_text("Instituição verificada com sucesso!")


# =====================================================
# TESTE 7 - RECEBER NOTIFICAÇÃO DE INTERESSE
# =====================================================

@pytest.mark.django_db(transaction=True)
def test_instituicao_visualiza_notificacao_de_interesse(
    page,
    live_server,
    escola_ui,
    perfil_colaborador_instituicao_ui,
    tabela_informacoes_instituicao_ui,
):

    from instituicao.models import InteresseOportunidade

    # Cria uma notificação válida para a escola.
    notificacao = InteresseOportunidade.objects.create(
        escola=escola_ui,
        colaborador=perfil_colaborador_instituicao_ui,
        oportunidade_id=1,
        materia="Matemática",
        tipo="aula",
        expira_em=timezone.now() + timedelta(hours=10),
    )

    abrir_selecao_instituicao(
        page,
        live_server,
        escola_ui,
    )

    selecionar_escola_no_navegador(
        page,
        escola_ui,
    )

    page.locator("#senha-instituicao").fill(
        escola_ui.telefone
    )

    # Aguarda a validação e a consulta das notificações.
    with page.expect_response(
        lambda resposta: (
            "/instituicao/verificar-instituicao/"
            in resposta.url
        )
    ) as resposta_verificacao, page.expect_response(
        lambda resposta: (
            "/instituicao/api/notificacoes-interesse/"
            in resposta.url
        )
    ) as resposta_notificacoes:

        page.locator(
            "#confirmar-senha-instituicao"
        ).click()

    assert resposta_verificacao.value.status == 200
    assert resposta_notificacoes.value.status == 200

    dados = resposta_notificacoes.value.json()

    assert dados["sucesso"] is True
    assert dados["total"] == 1

    assert dados["notificacoes"][0]["nome_colaborador"] == (
        "Colaborador Social Playwright"
    )

    assert dados["notificacoes"][0]["materia"] == "Matemática"

    # Confere a notificação na interface.
    cartao = page.locator(
        "#lista-notificacoes-interesse .interesse-notificacao"
    )

    expect(cartao).to_have_count(1)

    expect(cartao).to_contain_text(
        "Colaborador Social Playwright"
    )

    expect(cartao).to_contain_text("Matemática")
    expect(cartao).to_contain_text("Expira em")

    notificacao.refresh_from_db()

    assert notificacao.expira_em > timezone.now()