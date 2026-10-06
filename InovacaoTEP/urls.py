"""
URL configuration for InovacaoTEP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from InovacaoTEP.views import pagina_inicial

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pagina_inicial, name='pagina_inicial'),
    path('usuario/', include('usuario.urls')), 
    path('instituicao/', include('instituicao.urls')),
     # Inclua as URLs do aplicativo 'usuario'
]
