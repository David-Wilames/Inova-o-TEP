from django.urls import path

from . import views

urlpatterns = [
    path('', views.pagina_instituicao, name='pagina_instituicao'),
    path("adicionar/",views.adicionar_instituicao,name="adicionar_instituicao"),
    path("selecionar-escola/",views.selecionar_escola,name="selecionar_escola"),
    path("confirmar-escola/",views.confirmar_escola,name="confirmar_escola"),
    path("verificar-instituicao/",views.verificar_instituicao,name="verificar_instituicao",),
    path("excluir-registro/",views.excluir_registro_instituicao,name="excluir_registro_instituicao",),
    path("api/colaborador/<int:colaborador_id>/perfil/",views.perfil_colaborador_api,name="perfil_colaborador_api",),
    path("api/escolas/",views.listar_escolas,name="listar_escolas",),
]