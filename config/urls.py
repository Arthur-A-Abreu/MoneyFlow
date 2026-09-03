from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('', include('apps.dashboard.urls')),
    path('transactions/', include('apps.finance.urls')),
    path('insights/', include('apps.insights.urls')),
    path('reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customização do Django Admin
admin.site.site_header = 'MoneyFlow — Administração'
admin.site.site_title = 'MoneyFlow Admin'
admin.site.index_title = 'Painel de Administração'
