from django.db import models
from django.conf import settings
from django.utils.text import slugify
from apps.core.models import UserOwnedModel, UserOwnedManager


class Category(models.Model):
    """
    Categoria de movimentação financeira.
    Cada usuário possui suas próprias categorias — isolamento total.
    """
    TYPE_SCOPE_CHOICES = [
        ('INCOME', 'Receita'),
        ('EXPENSE', 'Despesa'),
        ('BOTH', 'Ambos'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Usuário',
    )
    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Slug', max_length=120, blank=True)
    color_hex = models.CharField(
        'Cor (HEX)',
        max_length=7,
        default='#6B7280',
        help_text='Cor hexadecimal para gráficos e badges.',
    )
    icon = models.CharField(
        'Ícone',
        max_length=50,
        default='bi-tag',
        help_text='Classe do Bootstrap Icons (ex: bi-cart-check).',
    )
    type_scope = models.CharField(
        'Tipo',
        max_length=10,
        choices=TYPE_SCOPE_CHOICES,
        default='EXPENSE',
        help_text='Define se a categoria aparece em receitas, despesas ou ambos.',
    )
    is_default = models.BooleanField(
        'Categoria padrão',
        default=False,
        help_text='Categorias padrão são criadas automaticamente para novos usuários.',
    )
    is_active = models.BooleanField('Ativa', default=True)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_category_per_user',
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def transaction_count(self):
        """Número de movimentações vinculadas a esta categoria."""
        return self.transactions.filter(is_deleted=False).count()


class Transaction(UserOwnedModel):
    """
    Movimentação financeira — o registro central do sistema.
    Tudo (receita e despesa) fica na mesma tabela, como um extrato bancário.
    """
    TYPE_CHOICES = [
        ('INCOME', 'Receita'),
        ('EXPENSE', 'Despesa'),
    ]

    STATUS_CHOICES = [
        ('COMPLETED', 'Concluída'),
        ('PENDING', 'Pendente'),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Categoria',
    )
    amount = models.DecimalField(
        'Valor',
        max_digits=12,
        decimal_places=2,
        help_text='Valor da movimentação em reais.',
    )
    transaction_type = models.CharField(
        'Tipo',
        max_length=10,
        choices=TYPE_CHOICES,
    )
    description = models.CharField(
        'Descrição',
        max_length=255,
        help_text='Breve descrição da movimentação.',
    )
    date = models.DateField(
        'Data',
        db_index=True,
    )
    status = models.CharField(
        'Status',
        max_length=10,
        choices=STATUS_CHOICES,
        default='COMPLETED',
    )
    notes = models.TextField(
        'Observações',
        blank=True,
        default='',
        help_text='Notas opcionais sobre a movimentação.',
    )

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date'], name='idx_transaction_user_date'),
            models.Index(fields=['user', 'transaction_type'], name='idx_transaction_user_type'),
            models.Index(fields=['user', 'category'], name='idx_transaction_user_cat'),
        ]

    def __str__(self):
        prefix = '+' if self.transaction_type == 'INCOME' else '-'
        return f'{prefix} R$ {self.amount} — {self.description}'

    @property
    def is_income(self):
        return self.transaction_type == 'INCOME'

    @property
    def is_expense(self):
        return self.transaction_type == 'EXPENSE'

    @property
    def signed_amount(self):
        """Retorna o valor com sinal: positivo para receita, negativo para despesa."""
        if self.transaction_type == 'INCOME':
            return self.amount
        return -self.amount
