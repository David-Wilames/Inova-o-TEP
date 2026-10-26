from datetime import timedelta

from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from usuario.models import InformacoesColaborador

from .models import Escolas, InteresseOportunidade


def pagina_instituicao(request):
    colaboradores = (
        InformacoesColaborador.objects.select_related("usuario")
        .all()
        .order_by("nome_completo")
    )

    return render(
        request,
        "instituicao/instituicao.html",
        {
            "colaboradores": colaboradores,
        },
    )


def adicionar_instituicao(request):
    escolas = Escolas.objects.all().order_by("nome_unidade_escolar")

    if request.method == "POST":
        escola_id = request.POST.get("escola")
        materia = request.POST.get("materia", "").strip()
        tipo = request.POST.get("tipo_aula", "").strip()
        quantidade = request.POST.get("quantidade", "").strip()
        responsavel = request.POST.get("responsavel", "").strip()
        observacoes = request.POST.get("observacoes", "").strip()

        # Verifica os campos obrigatórios.
        if not all([escola_id, materia, tipo, quantidade, responsavel]):
            messages.error(request, "Preencha todos os campos obrigatórios.")

        elif tipo not in ["aula", "horas"]:
            messages.error(request, "Selecione um tipo válido.")

        else:
            try:
                quantidade_numero = int(quantidade)

                if quantidade_numero < 1:
                    raise ValueError

                # Busca os dados da escola no banco.
                escola = Escolas.objects.get(pk=escola_id)

                # Salva na tabela existente.
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO "informacoes_instituicao" (
                            "Escola",
                            "Telefone",
                            "CEP",
                            "Endereço",
                            "Municipio",
                            "Bairro",
                            "Materia",
                            "Tipo",
                            "Quantidade",
                            "Nome do responsavel",
                            "Observacoes"
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            str(escola.nome_unidade_escolar or ""),
                            str(escola.telefone or ""),
                            str(escola.cep or ""),
                            str(escola.endereco or ""),
                            str(escola.municipio or ""),
                            str(escola.bairro_localidade or ""),
                            materia,
                            tipo,
                            str(quantidade_numero),
                            responsavel,
                            observacoes,
                        ],
                    )

                messages.success(
                    request, "Informações da instituição salvas com sucesso!"
                )

                # Evita reenviar o formulário ao atualizar a página.
                return redirect(request.path)

            except Escolas.DoesNotExist:
                messages.error(request, "A escola selecionada não foi encontrada.")

            except ValueError:
                messages.error(
                    request, "Informe uma quantidade válida, maior que zero."
                )

    return render(
        request,
        "instituicao/adicionar_instituicao.html",
        {"escolas": escolas},
    )


def selecionar_escola(request):
    escolas = Escolas.objects.all().order_by("nome_unidade_escolar")

    escola_id = request.session.get("escola_id")

    return render(
        request,
        "instituicao/selecionar_escola.html",
        {
            "escolas": escolas,
            "escola_id_selecionada": escola_id,
        },
    )


def confirmar_escola(request):
    if request.method == "POST":
        escola_id = request.POST.get("escola_id")

        if escola_id and Escolas.objects.filter(pk=escola_id).exists():
            request.session["escola_id"] = int(escola_id)

            messages.success(request, "Instituição selecionada com sucesso!")

            return redirect("selecionar_escola")

        messages.error(request, "Selecione uma instituição válida.")

    return redirect("selecionar_escola")


@require_POST
def verificar_instituicao(request):
    """
    Confere a instituição e a senha e retorna as informações
    cadastradas em informacoes_instituicao.
    """
    # Uma nova tentativa de validação precisa confirmar novamente o acesso.
    request.session.pop("escola_autenticada_id", None)

    escola_id = request.POST.get("escola_id", "").strip()
    senha = request.POST.get("senha", "").strip()

    if not escola_id or not senha:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Selecione uma instituição e informe a senha.",
            },
            status=400,
        )

    try:
        escola = Escolas.objects.get(pk=escola_id)
    except (Escolas.DoesNotExist, ValueError, TypeError):
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "A instituição selecionada não foi encontrada.",
            },
            status=404,
        )

    # A senha precisa corresponder ao telefone cadastrado da instituição.
    telefone_cadastrado = str(escola.telefone or "").strip()

    if senha != telefone_cadastrado:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Senha incorreta. Confira os dados e tente novamente.",
            },
            status=403,
        )

    # Busca somente os registros que correspondem à escola selecionada.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                rowid,
                "Escola",
                "Telefone",
                "CEP",
                "Endereço",
                "Municipio",
                "Bairro",
                "Materia",
                "Tipo",
                "Quantidade",
                "Nome do responsavel",
                "Observacoes"
            FROM "informacoes_instituicao"
            WHERE TRIM("Escola") = %s
            ORDER BY "Materia"
            """,
            [str(escola.nome_unidade_escolar).strip()],
        )

        colunas = [
            "id",
            "escola",
            "telefone",
            "cep",
            "endereco",
            "municipio",
            "bairro",
            "materia",
            "tipo",
            "quantidade",
            "responsavel",
            "observacoes",
        ]

        registros = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

    # Não enviamos o telefone da instituição na resposta.
    for registro in registros:
        registro.pop("telefone", None)

    request.session["escola_id"] = escola.pk
    request.session["escola_autenticada_id"] = escola.pk

    return JsonResponse(
        {
            "sucesso": True,
            "mensagem": "Instituição verificada com sucesso!",
            "nome_escola": escola.nome_unidade_escolar,
            "registros": registros,
        }
    )


@require_POST
def excluir_registro_instituicao(request):
    escola_id = request.POST.get("escola_id", "").strip()
    registro_id = request.POST.get("registro_id", "").strip()
    senha = request.POST.get("senha", "").strip()

    if not escola_id or not registro_id or not senha:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Informe a instituição, o registro e a senha.",
            },
            status=400,
        )

    try:
        registro_id = int(registro_id)
        escola = Escolas.objects.get(pk=escola_id)
    except (ValueError, TypeError, Escolas.DoesNotExist):
        return JsonResponse(
            {"sucesso": False, "mensagem": "Instituição ou registro inválido."},
            status=400,
        )

    # Mantém a verificação usada atualmente no projeto.
    senha_cadastrada = str(escola.telefone or "").strip()

    if not senha_cadastrada or senha != senha_cadastrada:
        return JsonResponse(
            {"sucesso": False, "mensagem": "Senha incorreta."},
            status=403,
        )

    # Confere também se o registro pertence à escola selecionada.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM "informacoes_instituicao"
            WHERE rowid = %s
              AND TRIM("Escola") = %s
            """,
            [
                registro_id,
                str(escola.nome_unidade_escolar).strip(),
            ],
        )
        quantidade_excluida = cursor.rowcount

    if quantidade_excluida == 0:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Registro não encontrado nesta instituição.",
            },
            status=404,
        )

    return JsonResponse({"sucesso": True, "mensagem": "Registro excluído com sucesso!"})


@require_GET
def perfil_colaborador_api(request, colaborador_id):
    """
    Retorna os dados do colaborador selecionado para a janela de perfil.
    """

    try:
        colaborador = InformacoesColaborador.objects.select_related("usuario").get(
            pk=colaborador_id
        )
    except InformacoesColaborador.DoesNotExist:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Colaborador não encontrado.",
            },
            status=404,
        )

    dados = {
        "id": colaborador.pk,
        "nome_completo": colaborador.nome_completo or "",
        "nome_social": colaborador.nome_social or "",
        "genero": colaborador.genero or "",
        "data_nascimento": (
            colaborador.data_nascimento.strftime("%d/%m/%Y")
            if colaborador.data_nascimento
            else ""
        ),
        "email": colaborador.email or "",
        "telefone": colaborador.telefone or "",
        "municipio": colaborador.municipio or "",
        "uf": colaborador.uf or "",
        "cep": colaborador.cep or "",
        "logradouro": colaborador.logradouro or "",
        "numero": colaborador.numero or "",
        "complemento": colaborador.complemento or "",
        "bairro": colaborador.bairro or "",
        "materia": colaborador.materia or "",
        "formacao": colaborador.formacao or "",
        "pos_graduacao": colaborador.pos_graduacao or "",
        "disciplinas": colaborador.disciplinas or [],
        "tempo_integral": colaborador.tempo_integral,
        "horario_inicio": (
            colaborador.horario_inicio.strftime("%H:%M")
            if colaborador.horario_inicio
            else ""
        ),
        "horario_fim": (
            colaborador.horario_fim.strftime("%H:%M") if colaborador.horario_fim else ""
        ),
        "possui_deficiencia": colaborador.possui_deficiencia or "",
        "necessidades_acessibilidade": (colaborador.necessidades_acessibilidade or ""),
        "observacoes": colaborador.observacoes or "",
    }

    return JsonResponse(
        {
            "sucesso": True,
            "colaborador": dados,
        }
    )


@require_GET
def listar_escolas(request):
    escolas = Escolas.objects.all().order_by("nome_unidade_escolar")

    dados = []

    for escola in escolas:
        nome = escola.nome_unidade_escolar

        # Corrige nomes armazenados ou retornados como bytes.
        if isinstance(nome, bytes):
            nome = nome.decode("utf-8", errors="replace")

        dados.append(
            {
                "id": escola.pk,
                "nome": nome,
            }
        )

    return JsonResponse(
        {
            "escolas": dados,
            "total": len(dados),
        }
    )

@require_POST
def registrar_interesse(request):
    """
    Registra o interesse de um colaborador em uma oportunidade.

    A instituição responsável é determinada no servidor,
    consultando a oportunidade original no banco de dados.
    """

    # O colaborador precisa estar logado.
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Entre na sua conta de colaborador para demonstrar interesse.",
            },
            status=401,
        )

    # Valida o ID da oportunidade recebido.
    oportunidade_id = request.POST.get("oportunidade_id", "").strip()

    try:
        oportunidade_id = int(oportunidade_id)

        if oportunidade_id < 1:
            raise ValueError

    except (ValueError, TypeError):
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "A oportunidade selecionada é inválida.",
            },
            status=400,
        )

    # Localiza a oportunidade na tabela já existente.
    # Utilizamos rowid porque informacoes_instituicao
    # é uma tabela existente que não possui um ID declarado
    # explicitamente no modelo Django apresentado.

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                TRIM("Escola"),
                COALESCE("Materia", ''),
                COALESCE("Tipo", '')
            FROM "informacoes_instituicao"
            WHERE rowid = %s
            LIMIT 1
            """,
            [oportunidade_id],
        )

        oportunidade = cursor.fetchone()

    if not oportunidade:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Esta oportunidade não existe mais.",
            },
            status=404,
        )

    nome_escola, materia, tipo = oportunidade

    nome_escola = str(nome_escola or "").strip()
    materia = str(materia or "").strip()
    tipo = str(tipo or "").strip()

    # Identifica a escola responsável pela oportunidade.
    # A escola é descoberta no servidor, não pelo ID
    # de escola enviado pelo navegador.

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM "Escolas"
            WHERE TRIM("nome_unidade_escolar") = %s COLLATE NOCASE
            LIMIT 1
            """,
            [nome_escola],
        )

        resultado_escola = cursor.fetchone()

    if not resultado_escola:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": (
                    "Não foi possível localizar a instituição "
                    "responsável por esta oportunidade."
                ),
            },
            status=404,
        )

    escola_id = resultado_escola[0]

    # Localiza o perfil ligado à conta que está logada.
    colaborador = (
        InformacoesColaborador.objects
        .select_related("usuario")
        .filter(usuario_id=usuario_id)
        .first()
    )

    if not colaborador:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": (
                    "Seu perfil de colaborador não foi encontrado. "
                    "Complete seu cadastro antes de demonstrar interesse."
                ),
            },
            status=400,
        )

    agora = timezone.now()

    # Impede que o mesmo colaborador envie repetidamente
    # a mesma notificação enquanto ela ainda estiver válida.

    notificacao_existente = InteresseOportunidade.objects.filter(
        escola_id=escola_id,
        colaborador=colaborador,
        oportunidade_id=oportunidade_id,
        expira_em__gt=agora,
    ).first()

    if notificacao_existente:
        return JsonResponse(
            {
                "sucesso": True,
                "mensagem": (
                    "Seu interesse já foi enviado. "
                    "A instituição poderá consultá-lo durante o período válido."
                ),
            }
        )

    # Registra a notificação com validade de 10 horas.
    notificacao = InteresseOportunidade.objects.create(
        escola_id=escola_id,
        colaborador=colaborador,
        oportunidade_id=oportunidade_id,
        materia=materia,
        tipo=tipo,
        expira_em=agora + timedelta(hours=10),
    )

    return JsonResponse(
        {
            "sucesso": True,
            "mensagem": (
                "Seu interesse foi enviado à instituição com sucesso!"
            ),
            "notificacao_id": notificacao.pk,
            "expira_em": notificacao.expira_em.isoformat(),
        },
        status=201,
    )

@require_GET
def listar_notificacoes_interesse(request):
    """
    Lista as notificações ainda válidas
    da instituição autenticada.
    """

    # Verifica qual instituição teve o acesso confirmado.
    escola_id = request.session.get("escola_autenticada_id")

    if not escola_id:
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": (
                    "Selecione sua instituição e confirme a senha "
                    "para consultar as notificações."
                ),
                "notificacoes": [],
                "total": 0,
            },
            status=403,
        )

    # Confirma que a instituição existe.
    try:
        escola = Escolas.objects.get(pk=escola_id)

    except (Escolas.DoesNotExist, ValueError, TypeError):
        request.session.pop("escola_autenticada_id", None)

        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Instituição não encontrada. Valide o acesso novamente.",
                "notificacoes": [],
                "total": 0,
            },
            status=403,
        )

    agora = timezone.now()

    # Exclui notificações expiradas.
    InteresseOportunidade.objects.filter(
        expira_em__lte=agora
    ).delete()

    # Consulta exclusivamente as notificações desta instituição.
    notificacoes_db = (
        InteresseOportunidade.objects
        .filter(
            escola=escola,
            expira_em__gt=agora,
        )
        .select_related("colaborador")
        .order_by("-criado_em")
    )

    notificacoes = []

    for notificacao in notificacoes_db:
        colaborador = notificacao.colaborador

        nome = (
            colaborador.nome_social
            or colaborador.nome_completo
            or "Colaborador"
        )

        notificacoes.append(
            {
                "id": notificacao.pk,
                "nome_colaborador": nome,
                "materia": notificacao.materia or "Não informada",
                "tipo": notificacao.tipo or "Não informado",
                "recebida_em": timezone.localtime(
                    notificacao.criado_em
                ).strftime("%d/%m/%Y às %H:%M"),
                "segundos_restantes": max(
                    0,
                    int(
                        (
                            notificacao.expira_em - agora
                        ).total_seconds()
                    ),
                ),
            }
        )

    return JsonResponse(
        {
            "sucesso": True,
            "instituicao": escola.nome_unidade_escolar,
            "notificacoes": notificacoes,
            "total": len(notificacoes),
        }
    )


    