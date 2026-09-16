from django.shortcuts import render

def pagina_inicial(request):
    return render(request, 'pagina_inicial.html')
def cadastro_colaborador(request):
    return render(request, 'usuarios/cadastro.html')