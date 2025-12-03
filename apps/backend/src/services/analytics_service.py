import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract, desc
from src.db.models.models import Transaction, Category
from src.utils.enums import TransactionType
from src.db.schemas import analytics as schemas

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def _get_month_range(self, year: int, month: int):
        """Helper to get start and end date of a specific month."""
        start_date = datetime.date(year, month, 1)
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        return start_date, end_date

    def get_summary_cards(self) -> schemas.DashboardSummary:
        """
        Calculates totals for Current Month vs Previous Month.
        """
        today = datetime.date.today()

        curr_start, curr_end = self._get_month_range(today.year, today.month)
        curr_income = self._sum_transactions(curr_start, curr_end, TransactionType.INCOME)
        curr_expense = self._sum_transactions(curr_start, curr_end, TransactionType.EXPENSE)

        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        prev_start, prev_end = self._get_month_range(last_month.year, last_month.month)
        prev_income = self._sum_transactions(prev_start, prev_end, TransactionType.INCOME)
        prev_expense = self._sum_transactions(prev_start, prev_end, TransactionType.EXPENSE)

        curr_savings = curr_income - curr_expense
        prev_savings = prev_income - prev_expense

        def calc_change(curr, prev):
            if prev == 0:
                return 100.0 if curr > 0 else 0.0
            return ((curr - prev) / prev) * 100

        total_balance = (
                                self.db.query(func.sum(Transaction.amount))
                                .filter(Transaction.transaction_type == TransactionType.INCOME).scalar() or 0
                        ) - (
                                self.db.query(func.sum(Transaction.amount))
                                .filter(Transaction.transaction_type == TransactionType.EXPENSE).scalar() or 0
                        )

        return schemas.DashboardSummary(
            total_balance=total_balance,
            total_income=curr_income,
            total_expense=curr_expense,
            total_savings=curr_savings,
            income_change_pct=calc_change(curr_income, prev_income),
            expense_change_pct=calc_change(curr_expense, prev_expense),
            savings_change_pct=calc_change(curr_savings, prev_savings)
        )

    def _sum_transactions(self, start, end, tx_type: TransactionType) -> int:
        return self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.created_at >= start,
            Transaction.created_at <= end,
            Transaction.transaction_type == tx_type
        ).scalar() or 0

    def get_spending_by_category(self) -> list[schemas.CategorySpending]:
        """
        Returns expense breakdown for the CURRENT month.
        """
        today = datetime.date.today()
        start_date, end_date = self._get_month_range(today.year, today.month)
        results = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label("total")
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.transaction_type == TransactionType.EXPENSE,
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
            .group_by(Category.name)
            .all()
        )
        total_expense_month = sum(r.total for r in results) or 1
        data = []
        for cat_name, total_amount in results:
            data.append(schemas.CategorySpending(
                category_name=cat_name,
                amount=total_amount,
                percentage=round((total_amount / total_expense_month) * 100, 2)
            ))

        return sorted(data, key=lambda x: x.amount, reverse=True)

    def get_monthly_evolution(self, months: int = 6) -> list[schemas.MonthlyEvolution]:
        """
        Returns Income vs Expense bars for the last N months.
        SQLite specific date grouping using strftime.
        """
        end_date = datetime.date.today()
        start_date = (end_date.replace(day=1) - datetime.timedelta(days=30 * months))
        query = (
            self.db.query(
                func.strftime("%Y-%m", Transaction.created_at).label("month_str"),
                func.sum(case((Transaction.transaction_type == TransactionType.INCOME, Transaction.amount), else_=0)).label("income"),
                func.sum(case((Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount), else_=0)).label("expense"),
            )
            .filter(Transaction.created_at >= start_date)
            .group_by("month_str")
            .order_by("month_str")
        )
        results = query.all()
        data = []
        for r in results:
            data.append(schemas.MonthlyEvolution(
                month=r.month_str,
                total_income=r.income or 0,
                total_expense=r.expense or 0,
                balance=(r.income or 0) - (r.expense or 0)
            ))

        return data