from django.urls import path
from . import views


urlpatterns = [
    path('', views.pagina_instituicao, name='pagina_instituicao'),
    path("adicionar/",views.adicionar_instituicao,name="adicionar_instituicao")
]