from django.contrib import admin
from apps.finance.models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin de categorias com isolamento total por usuário.
    Mesmo o superadmin só vê suas próprias categorias.
    """
    list_display = ('name', 'type_scope', 'color_hex', 'icon', 'is_default', 'is_active')
    list_filter = ('type_scope', 'is_default', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('slug',)

    def get_queryset(self, request):
        """Filtra categorias pelo usuário logado — privacidade total."""
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        """Associa automaticamente ao usuário logado."""
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin de movimentações com isolamento total por usuário.
    Ninguém (nem superadmin) vê dados de outros usuários.
    """
    list_display = ('description', 'formatted_amount', 'transaction_type', 'category', 'date', 'status')
    list_filter = ('transaction_type', 'status', 'date', 'category')
    search_fields = ('description', 'notes')
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')

    def get_queryset(self, request):
        """Filtra movimentações pelo usuário logado — privacidade total."""
        qs = super().get_queryset(request)
        return qs.filter(user=request.user, is_deleted=False)

    def save_model(self, request, obj, form, change):
        """Associa automaticamente ao usuário logado."""
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Exibe apenas categorias do usuário logado nos selects."""
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(user=request.user, is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description='Valor')
    def formatted_amount(self, obj):
        prefix = '+' if obj.transaction_type == 'INCOME' else '-'
        color = '#059669' if obj.transaction_type == 'INCOME' else '#DC2626'
        return f'<span style=\"color:{color};font-weight:600\">{prefix} R$ {obj.amount:,.2f}</span>'

    formatted_amount.allow_tags = True
