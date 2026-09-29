from django.shortcuts import render
from.models import Escolas

def pagina_instituicao(request):
    return render(request, 'instituicao/instituicao.html')

def adicionar_instituicao(request):

    return render(
        request,
        "instituicao/adicionar_instituicao.html"
    )

def adicionar_instituicao(request):

    escolas = Escolas.objects.all().order_by('nome_unidade_escolar')

    return render(
        request,
        'instituicao/adicionar_instituicao.html',
        {
            'escolas': escolas
        }
    )
# Create your views here.
