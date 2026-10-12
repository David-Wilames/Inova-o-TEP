from django.shortcuts import redirect, render

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
        informacoes = InformacoesColaborador.objects.get(
            usuario_id=usuario.pk
        )
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

    return render(
        request,
        "escolha.html"
    )


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

    return render(
        request,
        "usuarios/login_colaborador.html",
        {"form": form}
    )


def colaborador(request):

    return render(
        request,
        "usuarios/colaborador.html"
    )


def login_estituiçao(request):

    return render(
        request,
        "login_estituiçao.html"
    )


def cadastro_colaborador(request):

    if request.method == "POST":

        form = CadastroProfessorForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "login_colaborador"
            )

    else:

        form = CadastroProfessorForm()

    return render(
        request,
        "usuarios/cadastro.html",
        {"form": form}
    )


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
    informacoes, _criada = InformacoesColaborador.objects.get_or_create(
        usuario=usuario
    )

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
        informacoes.tempo_integral = (
            dados.get("tempo_integral") == "sim"
        )

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

    return render(
        request,
        "usuarios/avaliacoes.html"
    )
