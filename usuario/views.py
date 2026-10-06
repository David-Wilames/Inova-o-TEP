from django.shortcuts import redirect, render

from .forms import CadastroProfessorForm, LoginProfessorForm


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

    return render(
        request,
        "usuarios/adicionar_informacoes.html"
    )


def avaliacoes(request):

    return render(
        request,
        "usuarios/avaliacoes.html"
    )
