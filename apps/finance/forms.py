from django import forms
from apps.finance.models import Transaction, Category


class TransactionForm(forms.ModelForm):
    """
    Formulário de criação/edição de movimentações.
    Filtra categorias pelo tipo de transação selecionado.
    """
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'amount', 'description', 'date', 'status', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_transaction_type',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0,00',
                'step': '0.01',
                'min': '0.01',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Almoço no restaurante',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações opcionais...',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user, is_active=True
            )


class CategoryForm(forms.ModelForm):
    """Formulário de criação/edição de categorias."""
    class Meta:
        model = Category
        fields = ['name', 'color_hex', 'icon', 'type_scope']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da categoria',
            }),
            'color_hex': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'bi-tag',
            }),
            'type_scope': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
