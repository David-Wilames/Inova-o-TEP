from django.shortcuts import render

def escolha(request):
    return render(request, 'escolha.html')

def login_colaborador(request):
    return render(request, 'usuarios/login_colaborador.html')

def login_estituiçao(request):
    return render(request, 'login_estituiçao.html')

def cadastro_colaborador(request):
    return render(request, 'usuarios/cadastro.html')

# Create your views here.
