#Motor de Insights Financeiros Inteligentes.
#Analisa os dados do usuário e gera mensagens textuais acionáveis.
#Usa métodos estatísticos determinísticos — sem dependência de IA externa.

from django.db.models import Sum
from decimal import Decimal
from datetime import date
import calendar

from apps.finance.models import Transaction


def generate_insights(user, month, year):
    #Gera uma lista de insights inteligentes baseados nos dados financeiros do usuário.
    #Retorna uma lista de dicts com: type (success/warning/info/danger), icon, message.
    
    insights = []

    # Período atual
    first_day = date(year, month, 1)
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)

    # Período anterior
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    prev_first = date(prev_year, prev_month, 1)
    prev_last_num = calendar.monthrange(prev_year, prev_month)[1]
    prev_last = date(prev_year, prev_month, prev_last_num)

    # Movimentações
    qs = Transaction.objects.for_user(user)
    current_qs = qs.filter(date__gte=first_day, date__lte=last_day)
    prev_qs = qs.filter(date__gte=prev_first, date__lte=prev_last)

    # Totais
    income = current_qs.filter(transaction_type='INCOME').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    expense = current_qs.filter(transaction_type='EXPENSE').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    prev_income = prev_qs.filter(transaction_type='INCOME').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    prev_expense = prev_qs.filter(transaction_type='EXPENSE').aggregate(t=Sum('amount'))['t'] or Decimal('0')

    balance = income - expense
    prev_balance = prev_income - prev_expense

    # ──────────────────────────────────────────────────
    # 1. SCORE DE SAÚDE FINANCEIRA
    # ──────────────────────────────────────────────────
    if income > 0:
        savings_rate = float(balance / income * 100)
        if savings_rate >= 30:
            insights.append({
                'type': 'success',
                'icon': 'bi-trophy',
                'message': f'Excelente! Você está economizando {savings_rate:.0f}% da sua renda este mês. Continue assim! 🎉',
            })
        elif savings_rate >= 10:
            insights.append({
                'type': 'info',
                'icon': 'bi-piggy-bank',
                'message': f'Bom trabalho! Você está economizando {savings_rate:.0f}% da sua renda este mês.',
            })
        elif savings_rate >= 0:
            insights.append({
                'type': 'warning',
                'icon': 'bi-exclamation-triangle',
                'message': f'Atenção: sua taxa de economia está em apenas {savings_rate:.0f}%. Tente reduzir alguns gastos.',
            })
        else:
            insights.append({
                'type': 'danger',
                'icon': 'bi-exclamation-circle',
                'message': f'⚠️ Cuidado! Seus gastos estão superando sua renda em R$ {abs(balance):,.2f}.',
            })

    # ──────────────────────────────────────────────────
    # 2. COMPARAÇÃO COM MÊS ANTERIOR — ECONOMIA
    # ──────────────────────────────────────────────────
    if prev_balance != 0:
        diff = balance - prev_balance
        if diff > 0:
            insights.append({
                'type': 'success',
                'icon': 'bi-graph-up-arrow',
                'message': f'Você economizou R$ {diff:,.2f} a mais que no mês anterior. Ótimo progresso!',
            })
        elif diff < 0:
            insights.append({
                'type': 'warning',
                'icon': 'bi-graph-down-arrow',
                'message': f'Você economizou R$ {abs(diff):,.2f} a menos que no mês anterior.',
            })

    # ──────────────────────────────────────────────────
    # 3. VARIAÇÃO POR CATEGORIA (MoM)
    # ──────────────────────────────────────────────────
    current_by_cat = current_qs.filter(transaction_type='EXPENSE').values(
        'category__name'
    ).annotate(total=Sum('amount')).order_by('-total')

    prev_by_cat = {
        item['category__name']: item['total']
        for item in prev_qs.filter(transaction_type='EXPENSE').values(
            'category__name'
        ).annotate(total=Sum('amount'))
    }

    for cat in current_by_cat[:3]:  # Top 3 categorias
        cat_name = cat['category__name']
        cat_total = cat['total']
        prev_total = prev_by_cat.get(cat_name, Decimal('0'))

        if prev_total > 0:
            variation = float((cat_total - prev_total) / prev_total * 100)
            if variation > 15:
                insights.append({
                    'type': 'warning',
                    'icon': 'bi-arrow-up-right',
                    'message': f'Você gastou {variation:.0f}% a mais com {cat_name} em relação ao mês passado.',
                })
            elif variation < -15:
                insights.append({
                    'type': 'success',
                    'icon': 'bi-arrow-down-right',
                    'message': f'Parabéns! Você reduziu {abs(variation):.0f}% dos gastos com {cat_name}.',
                })

    # ──────────────────────────────────────────────────
    # 4. CATEGORIA DOMINANTE
    # ──────────────────────────────────────────────────
    if current_by_cat and expense > 0:
        top_cat = current_by_cat[0]
        pct = float(top_cat['total'] / expense * 100)
        insights.append({
            'type': 'info',
            'icon': 'bi-pie-chart',
            'message': f'Sua maior categoria de gastos este mês é "{top_cat["category__name"]}", representando {pct:.0f}% das suas despesas.',
        })

    # ──────────────────────────────────────────────────
    # 5. PROJEÇÃO DE FECHAMENTO DE MÊS (BURN-RATE)
    # ──────────────────────────────────────────────────
    today = date.today()
    if year == today.year and month == today.month and today.day > 1:
        days_elapsed = today.day
        days_in_month = last_day_num
        daily_expense = expense / days_elapsed
        projected_expense = daily_expense * days_in_month
        projected_balance = income - projected_expense

        insights.append({
            'type': 'info' if projected_balance >= 0 else 'danger',
            'icon': 'bi-calculator',
            'message': (
                f'No ritmo atual (R$ {daily_expense:,.2f}/dia), '
                f'a estimativa é fechar o mês com '
                f'{"saldo positivo" if projected_balance >= 0 else "deficit"} '
                f'de R$ {abs(projected_balance):,.2f}.'
            ),
        })

    # ──────────────────────────────────────────────────
    # 6. META DE ECONOMIA
    # ──────────────────────────────────────────────────
    if hasattr(user, 'profile') and user.profile.monthly_savings_target > 0:
        target = user.profile.monthly_savings_target
        if balance >= target:
            insights.append({
                'type': 'success',
                'icon': 'bi-bullseye',
                'message': f'🎯 Você atingiu sua meta de economia de R$ {target:,.2f}! Atual: R$ {balance:,.2f}.',
            })
        else:
            remaining = target - balance
            insights.append({
                'type': 'info',
                'icon': 'bi-bullseye',
                'message': f'Faltam R$ {remaining:,.2f} para atingir sua meta de economia de R$ {target:,.2f}.',
            })

    # Se não há dados suficientes
    if not insights:
        insights.append({
            'type': 'info',
            'icon': 'bi-lightbulb',
            'message': 'Comece registrando suas movimentações para receber insights personalizados!',
        })

    return insights
