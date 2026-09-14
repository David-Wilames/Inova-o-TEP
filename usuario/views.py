from django.shortcuts import render

def escolha(request):
    return render(request, 'escolha.html')

def login_colaborador(request):
    return render(request, 'login_colaborador.html')

def login_estituiçao(request):
    return render(request, 'login_estituiçao.html')

# Create your views here.
