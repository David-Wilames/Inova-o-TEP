from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Escolas


def pagina_instituicao(request):
    return render(request, "instituicao/instituicao.html")


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
            messages.error(
                request,
                "Preencha todos os campos obrigatórios."
            )

        elif tipo not in ["aula", "horas"]:
            messages.error(
                request,
                "Selecione um tipo válido."
            )

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
                    request,
                    "Informações da instituição salvas com sucesso!"
                )

                # Evita reenviar o formulário ao atualizar a página.
                return redirect(request.path)

            except Escolas.DoesNotExist:
                messages.error(
                    request,
                    "A escola selecionada não foi encontrada."
                )

            except ValueError:
                messages.error(
                    request,
                    "Informe uma quantidade válida, maior que zero."
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
        }
    )


def confirmar_escola(request):
    if request.method == "POST":
        escola_id = request.POST.get("escola_id")

        if escola_id and Escolas.objects.filter(pk=escola_id).exists():
            request.session["escola_id"] = int(escola_id)

            messages.success(
                request,
                "Instituição selecionada com sucesso!"
            )

            return redirect("selecionar_escola")

        messages.error(
            request,
            "Selecione uma instituição válida."
        )

    return redirect("selecionar_escola")

@require_POST
def verificar_instituicao(request):
    """
    Confere a instituição e a senha e retorna as informações
    cadastradas em informacoes_instituicao.
    """

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

        registros = [
            dict(zip(colunas, linha))
            for linha in cursor.fetchall()
        ]

    # Não enviamos o telefone da instituição na resposta.
    for registro in registros:
        registro.pop("telefone", None)

    request.session["escola_id"] = escola.pk

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
            {"sucesso": False, "mensagem": "Informe a instituição, o registro e a senha."},
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
            {"sucesso": False, "mensagem": "Registro não encontrado nesta instituição."},
            status=404,
        )

    return JsonResponse(
        {"sucesso": True, "mensagem": "Registro excluído com sucesso!"}
    )