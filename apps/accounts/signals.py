from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import User, UserProfile
from apps.finance.models import Category


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    #Cria automaticamente o perfil ao registrar um novo usuário.
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    #Salva o perfil quando o usuário é salvo.
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    #Cria categorias padrão para novos usuários.
    #Garante que todo usuário já comece com categorias úteis.
    if created:
        default_categories = [
            # Despesas
            {'name': 'Alimentação', 'color_hex': '#F59E0B', 'icon': 'bi-egg-fried', 'type_scope': 'EXPENSE'},
            {'name': 'Mercado', 'color_hex': '#10B981', 'icon': 'bi-cart-check', 'type_scope': 'EXPENSE'},
            {'name': 'Moradia', 'color_hex': '#6366F1', 'icon': 'bi-house-door', 'type_scope': 'EXPENSE'},
            {'name': 'Transporte', 'color_hex': '#3B82F6', 'icon': 'bi-car-front', 'type_scope': 'EXPENSE'},
            {'name': 'Saúde', 'color_hex': '#EF4444', 'icon': 'bi-heart-pulse', 'type_scope': 'EXPENSE'},
            {'name': 'Academia', 'color_hex': '#8B5CF6', 'icon': 'bi-bicycle', 'type_scope': 'EXPENSE'},
            {'name': 'Educação', 'color_hex': '#06B6D4', 'icon': 'bi-book', 'type_scope': 'EXPENSE'},
            {'name': 'Lazer', 'color_hex': '#EC4899', 'icon': 'bi-controller', 'type_scope': 'EXPENSE'},
            {'name': 'Dízimo', 'color_hex': '#D97706', 'icon': 'bi-heart', 'type_scope': 'EXPENSE'},
            {'name': 'Assinaturas', 'color_hex': '#7C3AED', 'icon': 'bi-credit-card', 'type_scope': 'EXPENSE'},
            {'name': 'Outros Gastos', 'color_hex': '#6B7280', 'icon': 'bi-three-dots', 'type_scope': 'EXPENSE'},
            # Receitas
            {'name': 'Salário', 'color_hex': '#059669', 'icon': 'bi-wallet2', 'type_scope': 'INCOME'},
            {'name': 'Freelance', 'color_hex': '#0D9488', 'icon': 'bi-laptop', 'type_scope': 'INCOME'},
            {'name': 'Investimentos', 'color_hex': '#2563EB', 'icon': 'bi-graph-up-arrow', 'type_scope': 'INCOME'},
            {'name': 'Outras Receitas', 'color_hex': '#16A34A', 'icon': 'bi-plus-circle', 'type_scope': 'INCOME'},
        ]

        categories = [
            Category(
                user=instance,
                name=cat['name'],
                color_hex=cat['color_hex'],
                icon=cat['icon'],
                type_scope=cat['type_scope'],
                is_default=True,
            )
            for cat in default_categories
        ]
        Category.objects.bulk_create(categories)
