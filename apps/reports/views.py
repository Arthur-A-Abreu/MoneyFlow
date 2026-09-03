from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime, date
import calendar

from apps.finance.models import Category
from apps.reports.services import (
    get_filtered_transactions,
    export_transactions_csv,
    export_transactions_excel,
    export_transactions_pdf,
)


@login_required
def report_generator_view(request):
    """
    Central de Geração de Relatórios Personalizados.
    Permite filtrar por período, tipo, categoria e exportar em PDF, Excel ou CSV.
    """
    today = date.today()
    
    # Defaults para o mês atual
    first_day_curr_month = date(today.year, today.month, 1).strftime('%Y-%m-%d')
    last_day_curr_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1]).strftime('%Y-%m-%d')
    
    date_from_str = request.GET.get('date_from', first_day_curr_month)
    date_to_str = request.GET.get('date_to', last_day_curr_month)
    category_id = request.GET.get('category', '')
    transaction_type = request.GET.get('type', '')
    export_format = request.GET.get('export', '')

    date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else None
    date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else None

    transactions = get_filtered_transactions(
        user=request.user,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id if category_id else None,
        transaction_type=transaction_type if transaction_type else None,
    )

    # Exportações
    if export_format == 'csv':
        content = export_transactions_csv(transactions)
        filename = f"relatorio_financeiro_{date.today().strftime('%Y%m%d')}.csv"
        response = HttpResponse(content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    elif export_format == 'excel':
        content = export_transactions_excel(transactions, request.user, date_from, date_to)
        filename = f"relatorio_financeiro_{date.today().strftime('%Y%m%d')}.xlsx"
        response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    elif export_format == 'pdf':
        content = export_transactions_pdf(transactions, request.user, date_from, date_to)
        filename = f"relatorio_financeiro_{date.today().strftime('%Y%m%d')}.pdf"
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response

    # Preview na tela
    categories = Category.objects.filter(user=request.user, is_active=True)
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'INCOME')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'EXPENSE')
    balance = total_income - total_expense

    context = {
        'transactions': transactions,
        'categories': categories,
        'date_from': date_from_str,
        'date_to': date_to_str,
        'category_id': category_id,
        'transaction_type': transaction_type,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }
    return render(request, 'reports/report_generator.html', context)
