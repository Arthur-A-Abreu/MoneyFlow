from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from apps.insights.services import generate_insights


@login_required
def insights_view(request):
    """
    Central de Análises e Insights Financeiros Inteligentes.
    Exibe diagnósticos de saúde financeira, comparativos MoM e projeções.
    """
    today = timezone.localdate()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    insights = generate_insights(
        user=request.user,
        month=selected_month,
        year=selected_year,
    )

    months = [
        (i, date(2000, i, 1).strftime('%B').capitalize()) for i in range(1, 13)
    ]
    years = list(range(today.year - 5, today.year + 2))

    context = {
        'insights': insights,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months,
        'years': years,
    }
    return render(request, 'insights/insights.html', context)
