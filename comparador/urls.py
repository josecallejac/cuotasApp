from django.urls import path
from . import views

app_name = 'comparador'

urlpatterns = [
    path('', views.index, name='index'),
    path('evento/<int:evento_id>/', views.evento_detalle, name='evento_detalle'),
    path('deporte/<slug:deporte_slug>/', views.eventos_por_deporte, name='eventos_por_deporte'),
    path('mejores-cuotas/', views.mejores_cuotas, name='mejores_cuotas'),
    path('buscar/', views.buscar, name='buscar'),
    path('casas-apuestas/', views.casas_apuestas, name='casas_apuestas'),
]
