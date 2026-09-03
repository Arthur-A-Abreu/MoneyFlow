from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date, timedelta
import calendar
import json
from decimal import Decimal

from apps.finance.models import Transaction, Category
from apps.insights.services import generate_insights


@login_required
def dashboard_view(request):
    """
    Dashboard principal — tela inicial após o login.
    Exibe cards de resumo, gráficos e insights inteligentes.
    """
    today = timezone.localdate()

    # Período selecionado (mês/ano)
    try:
        selected_month = int(str(request.GET.get('month', today.month)).replace('.', ''))
        selected_year = int(str(request.GET.get('year', today.year)).replace('.', ''))
    except ValueError:
        selected_month = today.month
        selected_year = today.year

    # Datas do período
    first_day = date(selected_year, selected_month, 1)
    last_day_num = calendar.monthrange(selected_year, selected_month)[1]
    last_day = date(selected_year, selected_month, last_day_num)

    # Mês anterior para comparação
    if selected_month == 1:
        prev_month = 12
        prev_year = selected_year - 1
    else:
        prev_month = selected_month - 1
        prev_year = selected_year

    prev_first_day = date(prev_year, prev_month, 1)
    prev_last_day_num = calendar.monthrange(prev_year, prev_month)[1]
    prev_last_day = date(prev_year, prev_month, prev_last_day_num)

    # ─────────────────────────────────────────────────────────────────
    # AGREGAÇÕES DO MÊS ATUAL
    # ─────────────────────────────────────────────────────────────────
    user_transactions = Transaction.objects.for_user(request.user)
    month_transactions = user_transactions.filter(date__gte=first_day, date__lte=last_day)

    total_income = month_transactions.filter(
        transaction_type='INCOME'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_expense = month_transactions.filter(
        transaction_type='EXPENSE'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    balance = total_income - total_expense
    savings_rate = (balance / total_income * 100) if total_income > 0 else Decimal('0')

    # ─────────────────────────────────────────────────────────────────
    # AGREGAÇÕES DO MÊS ANTERIOR (para comparação MoM)
    # ─────────────────────────────────────────────────────────────────
    prev_transactions = user_transactions.filter(date__gte=prev_first_day, date__lte=prev_last_day)

    prev_income = prev_transactions.filter(
        transaction_type='INCOME'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    prev_expense = prev_transactions.filter(
        transaction_type='EXPENSE'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    prev_balance = prev_income - prev_expense

    # Variações MoM (%)
    def calc_variation(current, previous):
        if previous > 0:
            return round(float((current - previous) / previous * 100), 1)
        return 0 if current == 0 else 100

    income_variation = calc_variation(total_income, prev_income)
    expense_variation = calc_variation(total_expense, prev_expense)
    balance_variation = calc_variation(balance, prev_balance) if prev_balance >= 0 else 0

    # ─────────────────────────────────────────────────────────────────
    # DADOS PARA GRÁFICOS (Chart.js)
    # ─────────────────────────────────────────────────────────────────

    # 1. Gastos por Categoria (Doughnut)
    expenses_by_category = month_transactions.filter(
        transaction_type='EXPENSE'
    ).values(
        'category__name', 'category__color_hex'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')

    category_labels = [item['category__name'] for item in expenses_by_category]
    category_data = [float(item['total']) for item in expenses_by_category]
    category_colors = [item['category__color_hex'] for item in expenses_by_category]

    # 2. Receita vs Despesa nos últimos 6 meses (Barras)
    monthly_comparison = []
    for i in range(5, -1, -1):
        m = selected_month - i
        y = selected_year
        while m <= 0:
            m += 12
            y -= 1
        fd = date(y, m, 1)
        ld_num = calendar.monthrange(y, m)[1]
        ld = date(y, m, ld_num)

        m_income = user_transactions.filter(
            date__gte=fd, date__lte=ld, transaction_type='INCOME'
        ).aggregate(total=Sum('amount'))['total'] or 0
        m_expense = user_transactions.filter(
            date__gte=fd, date__lte=ld, transaction_type='EXPENSE'
        ).aggregate(total=Sum('amount'))['total'] or 0

        month_name = fd.strftime('%b/%y')
        monthly_comparison.append({
            'label': month_name,
            'income': float(m_income),
            'expense': float(m_expense),
        })

    comparison_labels = [m['label'] for m in monthly_comparison]
    comparison_income = [m['income'] for m in monthly_comparison]
    comparison_expense = [m['expense'] for m in monthly_comparison]

    # 3. Evolução do Saldo (Linha)
    balance_evolution = []
    running_balance = Decimal('0')
    for m_data in monthly_comparison:
        running_balance += Decimal(str(m_data['income'])) - Decimal(str(m_data['expense']))
        balance_evolution.append(float(running_balance))

    # ─────────────────────────────────────────────────────────────────
    # INSIGHTS INTELIGENTES
    # ─────────────────────────────────────────────────────────────────
    insights = generate_insights(
        user=request.user,
        month=selected_month,
        year=selected_year,
    )

    # ─────────────────────────────────────────────────────────────────
    # ÚLTIMAS MOVIMENTAÇÕES
    # ─────────────────────────────────────────────────────────────────
    recent_transactions = month_transactions.select_related('category')[:10]

    # ─────────────────────────────────────────────────────────────────
    # NAVEGAÇÃO DE MESES
    # ─────────────────────────────────────────────────────────────────
    months = [
        (i, date(2000, i, 1).strftime('%B').capitalize()) for i in range(1, 13)
    ]
    years = list(range(today.year - 5, today.year + 2))

    context = {
        # Cards de resumo
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'savings_rate': round(savings_rate, 1),
        'income_variation': income_variation,
        'expense_variation': expense_variation,
        'balance_variation': balance_variation,

        # Gráficos (JSON para Chart.js)
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'category_colors': json.dumps(category_colors),
        'comparison_labels': json.dumps(comparison_labels),
        'comparison_income': json.dumps(comparison_income),
        'comparison_expense': json.dumps(comparison_expense),
        'balance_evolution': json.dumps(balance_evolution),

        # Insights
        'insights': insights,

        # Últimas movimentações
        'recent_transactions': recent_transactions,

        # Seletor de período
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months,
        'years': years,
    }
    return render(request, 'dashboard/dashboard.html', context)


def landing_view(request):
    """Página inicial / landing page para visitantes."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'landing.html')
