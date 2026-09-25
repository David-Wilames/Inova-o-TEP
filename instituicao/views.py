from django.shortcuts import render

def pagina_instituicao(request):
    return render(request, 'instituicao/instituicao.html')

def adicionar_instituicao(request):

    return render(
        request,
        "instituicao/adicionar_instituicao.html"
    )

# Create your views here.
