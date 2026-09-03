from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    #Admin customizado de usuários.
    #Superadmin pode gerenciar usuários (ativar/desativar).
    #Exibe perfil inline.
    #Filtros avançados por status.

    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # Ações customizadas para ativar/desativar em massa
    actions = ['activate_users', 'deactivate_users']

    @admin.action(description='✅ Ativar usuários selecionados')
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} usuário(s) ativado(s) com sucesso.')

    @admin.action(description='🚫 Desativar usuários selecionados')
    def deactivate_users(self, request, queryset):
        # Não desativar a si mesmo
        queryset = queryset.exclude(pk=request.user.pk)
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} usuário(s) desativado(s) com sucesso.')
