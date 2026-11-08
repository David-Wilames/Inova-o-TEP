from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import CadastroProfessorForm, LoginProfessorForm
from .models import InformacoesColaborador, Usuarios


# MOSTRA AS INFORMAÇÕES DO COLABORADOR CADASTRADO
def informacoes_colaborador(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login_colaborador")

    try:
        usuario = Usuarios.objects.get(pk=usuario_id)
    except Usuarios.DoesNotExist:
        request.session.flush()
        return redirect("login_colaborador")

    try:
        informacoes = InformacoesColaborador.objects.get(usuario_id=usuario.pk)
    except InformacoesColaborador.DoesNotExist:
        informacoes = None

    return render(
        request,
        "usuarios/informacoes_colaborador.html",
        {
            "usuario": usuario,
            "informacoes": informacoes,
        },
    )


def escolha(request):

    return render(request, "escolha.html")


def login_colaborador(request):

    if request.method == "POST":
        form = LoginProfessorForm(request.POST)

        if form.is_valid():
            # Usuário encontrado pelo username ou e-mail
            usuario = form.usuario

            # Guarda o ID do usuário na sessão
            request.session["usuario_id"] = usuario.id

            return redirect("colaborador")

    else:
        form = LoginProfessorForm()

    return render(request, "usuarios/login_colaborador.html", {"form": form})


def colaborador(request):
    oportunidades = []

    with connection.cursor() as cursor:
        # Verifica se a tabela existe no banco SQLite.
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'informacoes_instituicao'
        """)

        tabela_existe = cursor.fetchone()

        if tabela_existe:
            # Descobre os nomes reais das colunas.
            cursor.execute('PRAGMA table_info("informacoes_instituicao")')

            colunas = [coluna[1] for coluna in cursor.fetchall()]

            # Relaciona os nomes possíveis das colunas.
            aliases = {
                "escola": [
                    "Escola",
                    "escola",
                    "nome_escola",
                ],
                "materia": [
                    "Materia",
                    "materia",
                    "matéria",
                ],
                "tipo": [
                    "Tipo",
                    "tipo",
                ],
                "municipio": [
                    "Municipio",
                    "municipio",
                    "Município",
                    "municipio_escola",
                ],
                "telefone": [
                    "Telefone",
                    "telefone",
                ],
                "cep": [
                    "CEP",
                    "cep",
                ],
                "endereco": [
                    "Endereço",
                    "Endereco",
                    "endereco",
                    "logradouro",
                ],
                "bairro": [
                    "Bairro",
                    "bairro",
                ],
                "quantidade": [
                    "Quantidade",
                    "quantidade",
                ],
                "responsavel": [
                    "Nome do responsavel",
                    "Nome do responsável",
                    "nome_responsavel",
                    "responsavel",
                ],
                "observacoes": [
                    "Observacoes",
                    "Observações",
                    "observacoes",
                    "observacoes_escola",
                ],
            }

            # Escolhe apenas colunas que realmente existem.
            selecionadas = {}

            for destino, possibilidades in aliases.items():
                for nome in possibilidades:
                    if nome in colunas:
                        selecionadas[destino] = nome
                        break

            if "escola" in selecionadas:
                # IMPORTANTE:
                # O rowid identifica o registro original da oportunidade.
                # O HTML utilizará esse valor em oportunidade.id.
                campos_sql = ['rowid AS "id"']

                # Mantém os campos já utilizados no HTML.
                for destino, coluna in selecionadas.items():
                    coluna_segura = '"' + coluna.replace('"', '""') + '"'

                    campos_sql.append(f'{coluna_segura} AS "{destino}"')

                # Monta a consulta incluindo o identificador.
                sql = (
                    "SELECT "
                    + ", ".join(campos_sql)
                    + ' FROM "informacoes_instituicao"'
                    + " ORDER BY rowid DESC"
                )

                cursor.execute(sql)

                nomes = [descricao[0] for descricao in cursor.description]

                oportunidades = [dict(zip(nomes, linha)) for linha in cursor.fetchall()]

    return render(
        request,
        "usuarios/colaborador.html",
        {
            "oportunidades": oportunidades,
        },
    )


def login_estituiçao(request):

    return render(request, "login_estituiçao.html")


def cadastro_colaborador(request):

    if request.method == "POST":
        form = CadastroProfessorForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("login_colaborador")

    else:
        form = CadastroProfessorForm()

    return render(request, "usuarios/cadastro.html", {"form": form})


def adicionar_informacoes(request):
    from django.contrib import messages
    from django.shortcuts import redirect, render

    from .models import InformacoesColaborador, Usuarios

    # Verifica se existe um usuário conectado
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login_colaborador")

    # Busca o usuário cadastrado na tabela usuarios
    try:
        usuario = Usuarios.objects.get(id=usuario_id)
    except Usuarios.DoesNotExist:
        request.session.flush()
        return redirect("login_colaborador")

    # Procura informações já cadastradas para esse usuário
    informacoes, _criada = InformacoesColaborador.objects.get_or_create(usuario=usuario)

    if request.method == "POST":
        dados = request.POST

        # Dados pessoais
        informacoes.nome_completo = dados.get("nome_completo", "").strip()
        informacoes.nome_social = dados.get("nome_social", "").strip()
        informacoes.genero = dados.get("genero", "")
        informacoes.possui_deficiencia = dados.get("possui_deficiencia", "")
        informacoes.necessidades_acessibilidade = dados.get(
            "necessidades_acessibilidade", ""
        ).strip()

        # Data de nascimento
        data_nascimento = dados.get("data_nascimento", "")
        informacoes.data_nascimento = data_nascimento or None

        # Contato
        informacoes.email = dados.get("email", "").strip()
        informacoes.telefone = dados.get("telefone", "").strip()

        # Endereço
        informacoes.cep = dados.get("cep", "").strip()
        informacoes.numero = dados.get("numero", "").strip()
        informacoes.logradouro = dados.get("logradouro", "").strip()
        informacoes.complemento = dados.get("complemento", "").strip()
        informacoes.bairro = dados.get("bairro", "").strip()
        informacoes.municipio = dados.get("municipio", "").strip()
        informacoes.uf = dados.get("uf", "")

        # Documentos
        informacoes.tipo_documento = dados.get("tipo_documento", "")
        informacoes.rg = dados.get("rg", "").strip()
        informacoes.cpf = dados.get("cpf", "").strip()

        # Área de atuação
        informacoes.materia = dados.get("materia", "").strip()

        # Disponibilidade
        informacoes.tempo_integral = dados.get("tempo_integral") == "sim"

        horario_inicio = dados.get("horario_inicio", "")
        horario_fim = dados.get("horario_fim", "")

        informacoes.horario_inicio = horario_inicio or None
        informacoes.horario_fim = horario_fim or None

        # Formação
        informacoes.formacao = dados.get("formacao", "").strip()
        informacoes.pos_graduacao = dados.get("pos_graduacao", "").strip()

        # Disciplinas selecionadas
        disciplinas = dados.getlist("disciplinas")
        informacoes.disciplinas = disciplinas

        # Observações
        informacoes.observacoes = dados.get("observacoes", "").strip()

        # Salva os dados na tabela informacoes_colaborador
        informacoes.save()

        messages.success(request, "Informações salvas com sucesso!")

        return redirect("colaborador")

    return render(
        request,
        "usuarios/adicionar_informacoes.html",
        {"informacoes": informacoes},
    )


def avaliacoes(request):

    return render(request, "usuarios/avaliacoes.html")


@require_GET
def api_oportunidades_mapa(request):
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                "Escola",
                "CEP",
                "Endereço",
                "Municipio",
                "Bairro",
                "Materia",
                "Tipo",
                "Telefone",
                "Quantidade",
                "Observacoes"
            FROM "informacoes_instituicao"
        """)

        colunas = [coluna[0] for coluna in cursor.description]

        escolas = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

    oportunidades = []

    for escola in escolas:
        oportunidades.append(
            {
                "escola": escola.get("Escola") or "",
                "cep": escola.get("CEP") or "",
                "endereco": escola.get("Endereço") or "",
                "municipio": escola.get("Municipio") or "",
                "bairro": escola.get("Bairro") or "",
                "materia": escola.get("Materia") or "",
                "tipo": escola.get("Tipo") or "",
                "telefone": escola.get("Telefone") or "",
                "quantidade": escola.get("Quantidade") or "",
                "observacoes": escola.get("Observacoes") or "",
            }
        )

    return JsonResponse({"oportunidades": oportunidades})


@require_GET
def api_localizacao_colaborador(request):

    # Verificar se existe um colaborador autenticado.
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return JsonResponse({"erro": "Usuário não autenticado."}, status=401)

    # Buscar as informações cadastradas pelo colaborador.
    try:
        informacoes = InformacoesColaborador.objects.get(usuario_id=usuario_id)

    except InformacoesColaborador.DoesNotExist:
        return JsonResponse(
            {"erro": ("O colaborador ainda não cadastrou suas informações.")},
            status=404,
        )

    # Retornar os dados necessários para o mapa e o perfil profissional.
    return JsonResponse(
        {
            # Endereço: utilizado internamente para localizar o marcador.
            "cep": informacoes.cep or "",
            "logradouro": informacoes.logradouro or "",
            "numero": informacoes.numero or "",
            "bairro": informacoes.bairro or "",
            "municipio": informacoes.municipio or "",
            "uf": informacoes.uf or "",
            # Identificação profissional.
            "nome_completo": informacoes.nome_completo or "",
            "nome_social": informacoes.nome_social or "",
            # Informações profissionais.
            "materia": informacoes.materia or "",
            "formacao": informacoes.formacao or "",
            "pos_graduacao": informacoes.pos_graduacao or "",
            "disciplinas": informacoes.disciplinas or [],
            # Disponibilidade profissional.
            "tempo_integral": informacoes.tempo_integral,
            "horario_inicio": (
                informacoes.horario_inicio.strftime("%H:%M")
                if informacoes.horario_inicio
                else ""
            ),
            "horario_fim": (
                informacoes.horario_fim.strftime("%H:%M")
                if informacoes.horario_fim
                else ""
            ),
            # Observações profissionais.
            "observacoes": informacoes.observacoes or "",
        }
    )

@require_GET
def api_colaboradores_mapa(request):

    # Somente instituições autenticadas podem consultar os endereços.
    escola_id = request.session.get("escola_autenticada_id")

    if not escola_id:
        return JsonResponse(
            {"erro": "Instituição não autenticada."},
            status=403
        )

    # Buscar todos os colaboradores com perfil ativo.
    perfis = (
        InformacoesColaborador.objects
        .filter(perfil_ativo=True)
        .select_related("usuario")
        .exclude(logradouro__exact="")
        .order_by("nome_completo")
    )

    colaboradores = []

    for informacoes in perfis:

        nome = (
            informacoes.nome_social.strip()
            or informacoes.nome_completo.strip()
            or informacoes.usuario.nome_completo.strip()
        )

        colaboradores.append({
            "id": informacoes.id,
            "nome": nome,
            "logradouro": informacoes.logradouro,
            "numero": informacoes.numero,
            "complemento": informacoes.complemento,
            "bairro": informacoes.bairro,
            "municipio": informacoes.municipio,
            "uf": informacoes.uf,
            "cep": informacoes.cep,
            "materia": informacoes.materia,
        })

    return JsonResponse({
        "colaboradores": colaboradores,
        "total": len(colaboradores)
    })



@require_POST
def alternar_visibilidade_perfil(request):
    """
    Ativa ou desativa a visibilidade do perfil do colaborador
    para as instituições.
    """

    # Verifica qual usuário está conectado.
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login_colaborador")

    # Busca somente o perfil do usuário conectado.
    try:
        informacoes = InformacoesColaborador.objects.get(
            usuario_id=usuario_id
        )

    except InformacoesColaborador.DoesNotExist:
        return redirect("adicionar_informacoes")

    # Inverte o estado atual.
    informacoes.perfil_ativo = not informacoes.perfil_ativo

    # Salva a alteração no banco de dados.
    informacoes.save(update_fields=["perfil_ativo"])

    # Retorna à página do perfil.
    return redirect("informacoes_colaborador")
