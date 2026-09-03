from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    #Modelo de usuário customizado.
    #Permite login por email e extensão futura do modelo.
    
    email = models.EmailField('E-mail', unique=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.username


class UserProfile(models.Model):
    #Perfil estendido do usuário com preferências pessoais.
    #Criado automaticamente via signal ao registrar o usuário.
    
    THEME_CHOICES = [
        ('light', 'Claro'),
        ('dark', 'Escuro'),
        ('system', 'Sistema'),
    ]

    CURRENCY_CHOICES = [
        ('BRL', 'Real (R$)'),
        ('USD', 'Dólar (US$)'),
        ('EUR', 'Euro (€)'),
        ('ARS', 'Peso Argentino ($)'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário',
    )
    avatar = models.ImageField(
        'Avatar',
        upload_to='avatars/',
        blank=True,
        null=True,
    )
    currency = models.CharField(
        'Moeda',
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='BRL',
    )
    theme_preference = models.CharField(
        'Tema',
        max_length=10,
        choices=THEME_CHOICES,
        default='light',
    )
    monthly_savings_target = models.DecimalField(
        'Meta de Economia Mensal',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Meta opcional de economia mensal para cálculos de Insights.',
    )
    receive_monthly_email_report = models.BooleanField(
        'Receber relatório mensal por e-mail',
        default=True,
        help_text='Enviar automaticamente o relatório do mês por e-mail.',
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.user}'

    @property
    def currency_symbol(self):
        symbols = {'BRL': 'R$', 'USD': 'US$', 'EUR': '€', 'ARS': '$'}
        return symbols.get(self.currency, 'R$')
