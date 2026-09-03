from django import forms
from apps.accounts.models import User, UserProfile


class UserUpdateForm(forms.ModelForm):
    #Form para atualizar dados básicos do usuário.
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primeiro nome',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com',
            }),
        }


class UserProfileForm(forms.ModelForm):
    #Form para atualizar preferências do perfil.
    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'currency',
            'theme_preference',
            'monthly_savings_target',
            'receive_monthly_email_report',
        ]
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'theme_preference': forms.Select(attrs={'class': 'form-select'}),
            'monthly_savings_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0,00',
                'step': '0.01',
            }),
            'receive_monthly_email_report': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


from allauth.account.forms import LoginForm as AllauthLoginForm
from django.db import models


class CustomLoginForm(AllauthLoginForm):
    """
    Form de login customizado com mensagem amigável para contas pendentes de autorização por um Superadmin.
    """

    def clean(self):
        login = self.cleaned_data.get('login')
        password = self.cleaned_data.get('password')

        if login and password:
            user_qs = User.objects.filter(
                models.Q(email__iexact=login) | models.Q(username__iexact=login)
            )
            if user_qs.exists():
                user = user_qs.first()
                if user.check_password(password) and not user.is_active:
                    raise forms.ValidationError(
                        'Sua conta foi criada com sucesso, mas ainda está pendente de autorização por um Administrador.'
                    )

        return super().clean()

