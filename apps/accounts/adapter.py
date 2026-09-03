from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Adapter customizado do django-allauth para forçar que novas contas criadas
    fiquem com status 'is_active = False' até que um Superadministrador as aprove.
    """

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_active = False  # Requer aprovação do Superadmin
        if commit:
            user.save()
        return user

    def respond_user_signed_up(self, request, user):
        messages.success(
            request,
            'Sua conta foi criada com sucesso! Por motivos de segurança, ela precisa ser autorizada/aprovada por um Administrador antes que você possa acessar o painel.'
        )
        return redirect('account_login')
