"""
apps.core — Mixins base, managers e utilitários reutilizáveis.
"""
from django.db import models


class UserOwnedManager(models.Manager):
    """
    Manager customizado que filtra automaticamente por usuário.
    Garante isolamento total de dados entre usuários.
    """
    def for_user(self, user):
        return self.get_queryset().filter(user=user, is_deleted=False)

    def all_for_user(self, user):
        """Inclui soft-deleted para administração."""
        return self.get_queryset().filter(user=user)


class TimeStampedModel(models.Model):
    """Mixin abstrato com campos de auditoria temporal."""
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True


class UserOwnedModel(TimeStampedModel):
    """
    Mixin abstrato para modelos que pertencem a um usuário.
    Inclui soft delete e manager isolado.
    """
    from django.conf import settings
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='%(class)ss',
    )
    is_deleted = models.BooleanField('Excluído', default=False)

    objects = UserOwnedManager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Exclusão lógica do registro."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    def restore(self):
        """Restaura registro excluído logicamente."""
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])
