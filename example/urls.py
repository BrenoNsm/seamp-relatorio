# example/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path("", views.upload_excel, name='upload_excel'),
    path("salvar_dados/", views.salvar_dados, name='salvar_dados'),
    path("gerar_relatorios_municipios/", views.gerar_relatorios_municipios, name='gerar_relatorios_municipios'),
    path("relatorio_individual/", views.relatorio_individual, name='relatorio_individual'),
    path("relatorio_geral/", views.relatorio_geral, name='relatorio_geral'),
]