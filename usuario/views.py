from django.shortcuts import render, redirect
from .forms import CadastroProfessorForm, LoginProfessorForm
from django.contrib.auth import login


def escolha(request):
    return render(request, 'escolha.html')


def login_colaborador(request):

    if request.method == 'POST':

        form = LoginProfessorForm(
            request=request,
            data=request.POST
        )

        if form.is_valid():

            login(request, form.get_user())

            return redirect('colaborador')

    else:

        form = LoginProfessorForm(
            request=request
        )

    return render(
        request,
        'usuarios/login_colaborador.html',
        {'form': form},
    )


def colaborador(request):

    return render(
        request,
        'usuarios/colaborador.html'
    )


def login_estituiçao(request):

    return render(
        request,
        'login_estituiçao.html'
    )


def cadastro_colaborador(request):

    if request.method == 'POST':

        form = CadastroProfessorForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('login_colaborador')

    else:

        form = CadastroProfessorForm()

    return render(
        request,
        'usuarios/cadastro.html',
        {'form': form}
    )

def adicionar_informacoes (request):
    return render(
        request,
        'usuarios/adicionar_informacoes.html'
    )