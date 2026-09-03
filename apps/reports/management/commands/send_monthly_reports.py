from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import date
import calendar

from apps.accounts.models import User
from apps.reports.services import get_filtered_transactions, export_transactions_pdf


class Command(BaseCommand):
    help = 'Envia relatório financeiro mensal em PDF por e-mail para todos os usuários ativos com a opção habilitada.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        
        # Mês anterior
        if today.month == 1:
            report_month = 12
            report_year = today.year - 1
        else:
            report_month = today.month - 1
            report_year = today.year

        first_day = date(report_year, report_month, 1)
        last_day_num = calendar.monthrange(report_year, report_month)[1]
        last_day = date(report_year, report_month, last_day_num)

        month_name = first_day.strftime('%B/%Y')
        self.stdout.write(self.style.NOTICE(f'Iniciando envio de relatórios do mês {month_name}...'))

        users = User.objects.filter(is_active=True, profile__receive_monthly_email_report=True)
        count = 0

        for user in users:
            transactions = get_filtered_transactions(
                user=user,
                date_from=first_day,
                date_to=last_day
            )

            if not transactions.exists():
                self.stdout.write(f'Usuário {user.email} não possui movimentações em {month_name}. Pulando...')
                continue

            pdf_content = export_transactions_pdf(transactions, user, first_day, last_day)

            subject = f"Seu Extrato Financeiro Mensal — {month_name} | MoneyFlow"
            body = f"""Olá, {user.first_name or user.username}!

Seu extrato financeiro consolidado do mês de {month_name} foi gerado com sucesso pelo MoneyFlow.

Em anexo, você encontrará seu relatório completo em formato PDF com todas as suas movimentações, receitas, despesas e saldo final do período.

Acesse sua conta para ver seus insights inteligentes atualizados: http://localhost:8000/dashboard/

Atenciosamente,
Equipe MoneyFlow
"""

            email = EmailMessage(
                subject=subject,
                body=body,
                from_email='MoneyFlow <noreply@moneyflow.com>',
                to=[user.email],
            )
            email.attach(
                filename=f"extrato_financeiro_{report_year}_{report_month:02d}.pdf",
                content=pdf_content,
                mimetype='application/pdf'
            )
            email.send(fail_silently=False)
            count += 1
            self.stdout.write(self.style.SUCCESS(f'Relatório enviado com sucesso para {user.email}'))

        self.stdout.write(self.style.SUCCESS(f'Concluído! Total de {count} relatórios enviados.'))
