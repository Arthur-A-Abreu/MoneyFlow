from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from datetime import date

from apps.accounts.models import User
from apps.finance.models import Category, Transaction
from apps.insights.services import generate_insights
from apps.reports.services import export_transactions_csv, export_transactions_excel, export_transactions_pdf


class FinancialSystemTests(TestCase):
    def setUp(self):
        # Usuário 1
        self.user1 = User.objects.create_user(
            username='user1', email='user1@test.com', password='password123'
        )
        # Usuário 2
        self.user2 = User.objects.create_user(
            username='user2', email='user2@test.com', password='password123'
        )

        # Categorias já são criadas via post_save signal
        self.cat1 = Category.objects.filter(user=self.user1, type_scope='EXPENSE').first()
        self.cat2 = Category.objects.filter(user=self.user2, type_scope='EXPENSE').first()

        # Transações do Usuário 1
        self.t1 = Transaction.objects.create(
            user=self.user1,
            category=self.cat1,
            amount=Decimal('150.00'),
            transaction_type='EXPENSE',
            description='Gasto Secreto do User 1',
            date=date.today(),
            status='COMPLETED'
        )

        # Transações do Usuário 2
        self.t2 = Transaction.objects.create(
            user=self.user2,
            category=self.cat2,
            amount=Decimal('300.00'),
            transaction_type='EXPENSE',
            description='Gasto Secreto do User 2',
            date=date.today(),
            status='COMPLETED'
        )

    def test_user_data_isolation(self):
        """Verifica isolamento absoluto de dados entre usuários."""
        user1_transactions = Transaction.objects.for_user(self.user1)
        user2_transactions = Transaction.objects.for_user(self.user2)

        self.assertIn(self.t1, user1_transactions)
        self.assertNotIn(self.t2, user1_transactions)

        self.assertIn(self.t2, user2_transactions)
        self.assertNotIn(self.t1, user2_transactions)

    def test_soft_delete_and_capslock_safeguard(self):
        """Verifica que a transação é ocultada com soft delete."""
        self.t1.soft_delete()
        self.assertTrue(self.t1.is_deleted)
        
        # Não deve aparecer no for_user
        active = Transaction.objects.for_user(self.user1)
        self.assertNotIn(self.t1, active)

    def test_insights_generation(self):
        """Verifica se o motor de insights gera diagnósticos válidos."""
        insights = generate_insights(self.user1, date.today().month, date.today().year)
        self.assertIsInstance(insights, list)
        self.assertTrue(len(insights) > 0)

    def test_reports_generation(self):
        """Verifica exportação de CSV, Excel e PDF sem erros."""
        qs = Transaction.objects.for_user(self.user1)
        
        csv_data = export_transactions_csv(qs)
        self.assertTrue(len(csv_data) > 0)

        xlsx_data = export_transactions_excel(qs, self.user1)
        self.assertTrue(len(xlsx_data) > 0)

        pdf_data = export_transactions_pdf(qs, self.user1)
        self.assertTrue(len(pdf_data) > 0)
