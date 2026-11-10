
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('produtos/', views.produtos, name='produtos'),
    path('produtos/cadastrar/', views.cadastrar_produto, name='cadastrar_produto'),
    path('produtos/consultar/', views.consultar, name='consultar'),

    path('operacao/<str:tipo>/', views.operacao, name='operacao'),

    path('liberar/', views.liberar, name='liberar'),
]
