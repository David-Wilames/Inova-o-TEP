from django.urls import path
from . import views

urlpatterns = [
    path('escolha/', views.escolha, name='escolha'),
    path('login/colaborador/', views.login_colaborador, name='login_colaborador'),
    path('login/estituiçao/', views.login_estituiçao, name='login_estituiçao'),
]