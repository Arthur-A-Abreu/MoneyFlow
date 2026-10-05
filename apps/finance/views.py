import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.finance.models import Transaction, Category
from apps.finance.forms import TransactionForm, CategoryForm




# ==============================================================================
# MOVIMENTAÇÕES (TRANSACTIONS)
# ==============================================================================

@login_required
def transaction_list(request):
    """
    Lista de movimentações com filtros, busca e paginação.
    Extrato unificado — receitas e despesas juntas.
    """
    transactions = Transaction.objects.for_user(request.user)

    # Filtros
    transaction_type = request.GET.get('type', '')
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if status:
        transactions = transactions.filter(status=status)
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) | Q(notes__icontains=search)
        )

    # Paginação
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)

    # Categorias do usuário para o filtro
    categories = Category.objects.filter(user=request.user, is_active=True)

    context = {
        'transactions': transactions,
        'categories': categories,
        'current_filters': {
            'type': transaction_type,
            'category': category_id,
            'status': status,
            'date_from': date_from,
            'date_to': date_to,
            'search': search,
        },
    }
    return render(request, 'finance/transaction_list.html', context)


@login_required
def transaction_create(request):
    """Cria uma nova movimentação."""
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Movimentação registrada com sucesso!')
            return redirect('finance:transaction_list')
    else:
        form = TransactionForm(user=request.user)

    return render(request, 'finance/transaction_form.html', {
        'form': form,
        'title': 'Nova Movimentação',
    })


@login_required
def transaction_edit(request, pk):
    """Edita uma movimentação existente do usuário."""
    transaction = get_object_or_404(
        Transaction, pk=pk, user=request.user, is_deleted=False
    )
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Movimentação atualizada com sucesso!')
            return redirect('finance:transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    return render(request, 'finance/transaction_form.html', {
        'form': form,
        'title': 'Editar Movimentação',
        'transaction': transaction,
    })


@login_required
def transaction_delete(request, pk):
    """
    Soft delete de uma movimentação.
    Requer confirmação digitando 'DELETAR'.
    """
    transaction = get_object_or_404(
        Transaction, pk=pk, user=request.user, is_deleted=False
    )
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', '')
        if confirmation == 'DELETAR':
            transaction.soft_delete()
            messages.success(request, 'Movimentação excluída com sucesso!')
            return redirect('finance:transaction_list')
        else:
            messages.error(request, 'Digite "DELETAR" em maiúsculas para confirmar a exclusão.')

    return render(request, 'finance/transaction_confirm_delete.html', {
        'transaction': transaction,
    })


# ==============================================================================
# CATEGORIAS
# ==============================================================================

@login_required
def category_list(request):
    """Lista de categorias do usuário."""
    categories = Category.objects.filter(user=request.user, is_active=True)
    return render(request, 'finance/category_list.html', {
        'categories': categories,
    })


@login_required
def category_create(request):
    """Cria uma nova categoria."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Categoria "{category.name}" criada com sucesso!')
            return redirect('finance:category_list')
    else:
        form = CategoryForm()

    return render(request, 'finance/category_form.html', {
        'form': form,
        'title': 'Nova Categoria',
    })


@login_required
def category_edit(request, pk):
    """Edita uma categoria do usuário."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoria "{category.name}" atualizada!')
            return redirect('finance:category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'finance/category_form.html', {
        'form': form,
        'title': 'Editar Categoria',
        'category': category,
    })


@login_required
def category_delete(request, pk):
    """
    Desativa uma categoria (não exclui para manter integridade de dados).
    Requer confirmação digitando 'DELETAR'.
    """
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', '')
        if confirmation == 'DELETAR':
            if category.transaction_count > 0:
                category.is_active = False
                category.save()
                messages.warning(
                    request,
                    f'Categoria "{category.name}" desativada (possui {category.transaction_count} movimentações vinculadas).'
                )
            else:
                category.delete()
        else:
            messages.error(request, 'Digite "DELETAR" em maiúsculas para confirmar a exclusão.')
            return redirect('finance:category_list')

    return render(request, 'finance/category_confirm_delete.html', {
        'category': category,
    })


