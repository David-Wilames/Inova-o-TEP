from django.urls import path

from . import views

urlpatterns = [
    path('escolha/', views.escolha, name='escolha'),
    path('login/colaborador/', views.login_colaborador, name='login_colaborador'),
    path('login/estituiçao/', views.login_estituiçao, name='login_estituiçao'),
    path('cadastro/colaborador/', views.cadastro_colaborador, name='cadastro_colaborador'),
    path('colaborador/', views.colaborador, name='colaborador'),
    path('adicionar-informacoes/',views.adicionar_informacoes,name='adicionar_informacoes'),
    path('avaliacoes/', views.avaliacoes, name='avaliacoes'),
    path('colaborador/informacoes/', views.informacoes_colaborador, name='informacoes_colaborador'),
    path('api/oportunidades/mapa/', views.api_oportunidades_mapa, name='api_oportunidades_mapa'),
    path('api/localizacao-colaborador/',views.api_localizacao_colaborador,name='api_localizacao_colaborador'),
    path("colaborador/alternar-visibilidade/",views.alternar_visibilidade_perfil,name="alternar_visibilidade_perfil",),
    path("api/colaboradores-mapa/",views.api_colaboradores_mapa,name="api_colaboradores_mapa"),
]