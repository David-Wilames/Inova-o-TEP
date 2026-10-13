from django.contrib import messages
from django.db import connection
from django.shortcuts import redirect, render

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