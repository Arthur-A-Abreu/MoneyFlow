from django.urls import path
from apps.finance import views

app_name = 'finance'

urlpatterns = [
    # Movimentações
    path('', views.transaction_list, name='transaction_list'),
    path('new/', views.transaction_create, name='transaction_create'),
    path('<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # Importação com IA (Faturas / Extratos)
    path('import/', views.ai_import_page, name='ai_import_page'),
    path('import/process/', views.ai_process_statement, name='ai_process_statement'),
    path('import/save/', views.ai_bulk_save, name='ai_bulk_save'),

    # Categorias
    path('categories/', views.category_list, name='category_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]

