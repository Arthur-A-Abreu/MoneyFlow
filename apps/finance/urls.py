from django.urls import path
from apps.finance import views

app_name = 'finance'

urlpatterns = [
    # Movimentações
    path('', views.transaction_list, name='transaction_list'),
    path('new/', views.transaction_create, name='transaction_create'),
    path('<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # Categorias
    path('categories/', views.category_list, name='category_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
