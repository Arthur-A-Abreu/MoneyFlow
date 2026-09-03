from django.urls import path
from apps.insights import views

app_name = 'insights'

urlpatterns = [
    path('', views.insights_view, name='index'),
]
