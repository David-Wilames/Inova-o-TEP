from django.urls import path
from . import views

urlpatterns = [
    path('escolha/', views.escolha, name='escolha'),
    path('login/colaborador/', views.login_colaborador, name='login_colaborador'),
    path('login/estituiçao/', views.login_estituiçao, name='login_estituiçao'),
    path('cadastro/colaborador/', views.cadastro_colaborador, name='cadastro_colaborador'),
    path('colaborador/', views.colaborador, name='colaborador'),
    path('adicionar-informacoes/',views.adicionar_informacoes,name='adicionar_informacoes'),
]