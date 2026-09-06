from typing import Sequence
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.finance import Transaction, Budget, RecurringTransaction

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def get_by_type(self, user_id: int, type_: str, offset: int = 0, limit: int = 10) -> Sequence[Transaction]:
        stmt = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.type == type_,
            Transaction.is_deleted == False
        ).order_by(Transaction.date.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_date_range(self, user_id: int, date_from: datetime, date_to: datetime, type_: str | None = None, offset: int = 0, limit: int = 10) -> Sequence[Transaction]:
        stmt = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.date >= date_from,
            Transaction.date <= date_to
        )
        if type_:
            stmt = stmt.where(Transaction.type == type_)
        stmt = stmt.order_by(Transaction.date.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_category(self, user_id: int, category_id: int, offset: int = 0, limit: int = 10) -> Sequence[Transaction]:
        stmt = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            Transaction.is_deleted == False
        ).order_by(Transaction.date.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_transaction(
        self,
        user_id: int,
        amount: float | Decimal,
        type: str = "expense",
        category: str | None = None,
        category_id: int | None = None,
        description: str | None = None,
        date: date | datetime | None = None,
        currency: str = "UZS",
        **kwargs
    ) -> Transaction:
        if isinstance(date, datetime):
            target_date = date.date()
        elif isinstance(date, date):
            target_date = date
        else:
            target_date = datetime.utcnow().date()

        desc = description or ""
        if category and not category_id and f"[{category}]" not in desc:
            desc = f"[{category}] {desc}".strip()

        return await self.create(
            user_id=user_id,
            amount=Decimal(str(amount)),
            type=type,
            category_id=category_id,
            description=desc,
            date=target_date,
            currency=currency
        )

    async def get_balance(self, user_id: int, currency: str = "UZS") -> Decimal:
        stmt_income = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.currency == currency,
            Transaction.type == 'income',
            Transaction.is_deleted == False
        )
        stmt_expense = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.currency == currency,
            Transaction.type == 'expense',
            Transaction.is_deleted == False
        )
        
        income_sum = (await self.session.execute(stmt_income)).scalar() or Decimal('0.0')
        expense_sum = (await self.session.execute(stmt_expense)).scalar() or Decimal('0.0')
        
        return income_sum - expense_sum

    async def get_period_summary(self, user_id: int, start_date: datetime | date, end_date: datetime | date) -> dict:
        d_from = start_date.date() if isinstance(start_date, datetime) else start_date
        d_to = end_date.date() if isinstance(end_date, datetime) else end_date
        totals = await self.get_period_totals(user_id, d_from, d_to)
        return {
            "income": float(totals["income_total"]),
            "expense": float(totals["expense_total"]),
            "balance": float(totals["income_total"] - totals["expense_total"])
        }

    async def get_monthly_report(self, user_id: int, year: int, month: int) -> dict:
        import calendar
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        summary = await self.get_period_summary(user_id, start_date, end_date)
        summary["year"] = year
        summary["month"] = month
        return summary

    async def get_yearly_report(self, user_id: int, year: int) -> dict:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        summary = await self.get_period_summary(user_id, start_date, end_date)
        summary["year"] = year
        return summary


    async def get_period_totals(self, user_id: int, date_from: datetime, date_to: datetime) -> dict:
        stmt = select(Transaction.type, func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.date >= date_from,
            Transaction.date <= date_to
        ).group_by(Transaction.type)
        
        result = await self.session.execute(stmt)
        totals = dict(result.all())
        return {
            "income_total": totals.get('income', Decimal('0.0')),
            "expense_total": totals.get('expense', Decimal('0.0'))
        }

    async def get_category_breakdown(self, user_id: int, type_: str, date_from: datetime, date_to: datetime) -> list[dict]:
        stmt = select(Transaction.category_id, func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.type == type_,
            Transaction.is_deleted == False,
            Transaction.date >= date_from,
            Transaction.date <= date_to
        ).group_by(Transaction.category_id)
        
        result = await self.session.execute(stmt)
        return [{"category_id": row[0], "amount": row[1]} for row in result.all()]


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Budget)

    async def get_active_budgets(self, user_id: int) -> list[Budget]:
        stmt = select(Budget).where(
            Budget.user_id == user_id,
            Budget.is_active == True,
            Budget.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_budget_spending(self, user_id: int, budget_id: int, period_start: datetime, period_end: datetime) -> Decimal:
        budget = await self.get_by_id(budget_id)
        if not budget or budget.user_id != user_id:
            return Decimal('0.0')
        
        stmt = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.category_id == budget.category_id,
            Transaction.type == 'expense',
            Transaction.date >= period_start,
            Transaction.date <= period_end,
            Transaction.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar() or Decimal('0.0')


class RecurringTransactionRepository(BaseRepository[RecurringTransaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RecurringTransaction)

    async def get_due_transactions(self, check_date: date) -> list[RecurringTransaction]:
        stmt = select(RecurringTransaction).where(
            RecurringTransaction.is_active == True,
            RecurringTransaction.is_deleted == False,
            RecurringTransaction.next_date <= check_date
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

# Aliases
FinanceRepository = TransactionRepository

