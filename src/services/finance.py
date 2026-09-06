import structlog
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.finance import FinanceRepository
from src.models.finance import Transaction, Budget

logger = structlog.get_logger(__name__)

class FinanceService:
    """Service for managing finances."""
    def __init__(self, session_or_repo):
        if isinstance(session_or_repo, AsyncSession):
            self.session = session_or_repo
            self.repo = FinanceRepository(self.session)
        else:
            self.repo = session_or_repo
            self.session = getattr(session_or_repo, "session", None)

    async def add_transaction(self, user_id: int, amount: float, category: str, type: str, description: Optional[str] = None) -> Transaction:
        """Add a new transaction."""
        try:
            tx = await self.repo.create_transaction(
                user_id=user_id,
                amount=amount,
                category=category,
                type=type,
                description=description,
                date=datetime.now(timezone.utc)
            )
            if self.session:
                await self.session.commit()
            return tx
        except Exception as e:
            if self.session:
                await self.session.rollback()
            logger.error("Tranzaksiya qo'shishda xatolik", error=str(e))
            raise

    async def add_income(self, user_id: int, amount: float, category: str = "Umumiy", description: Optional[str] = None) -> Transaction:
        """Helper to add income transaction."""
        return await self.add_transaction(user_id, amount, category, "income", description)

    async def add_expense(self, user_id: int, amount: float, category: str = "Umumiy", description: Optional[str] = None) -> Transaction:
        """Helper to add expense transaction."""
        return await self.add_transaction(user_id, amount, category, "expense", description)

    async def parse_and_create(self, user_id: int, text: str) -> Transaction:
        """Parse quick string like '50000 tushlik +' or '25000 taksi -' and create transaction."""
        parts = text.strip().split()
        if not parts:
            raise ValueError("Bo'sh matn")
        
        amount = float(parts[0])
        tx_type = "expense"
        desc_parts = parts[1:]
        if desc_parts and desc_parts[-1] in ("+", "income"):
            tx_type = "income"
            desc_parts = desc_parts[:-1]
        elif desc_parts and desc_parts[-1] in ("-", "expense"):
            tx_type = "expense"
            desc_parts = desc_parts[:-1]
            
        desc = " ".join(desc_parts) if desc_parts else "Tezkor amal"
        return await self.add_transaction(user_id, amount, desc, tx_type, desc)

    async def get_balance(self, user_id: int) -> float:
        """Get current balance."""
        val = await self.repo.get_balance(user_id)
        return float(val)


    async def get_period_summary(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get summary for a period."""
        return await self.repo.get_period_summary(user_id, start_date, end_date)

    async def get_category_breakdown(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get category breakdown."""
        return await self.repo.get_category_breakdown(user_id, start_date, end_date)

    async def get_monthly_report(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Get monthly report."""
        return await self.repo.get_monthly_report(user_id, year, month)

    async def get_yearly_report(self, user_id: int, year: int) -> Dict[str, Any]:
        """Get yearly report."""
        return await self.repo.get_yearly_report(user_id, year)

    async def compare_periods(self, user_id: int, period1: tuple, period2: tuple) -> Dict[str, Any]:
        """Compare two periods."""
        p1_data = await self.get_period_summary(user_id, period1[0], period1[1])
        p2_data = await self.get_period_summary(user_id, period2[0], period2[1])
        return {"period1": p1_data, "period2": p2_data}

    async def trends(self, user_id: int) -> Dict[str, Any]:
        """Get trends."""
        return await self.repo.get_trends(user_id)

    async def create_budget(self, user_id: int, category: str, limit: float, period: str) -> Budget:
        """Create a budget."""
        budget = await self.repo.create_budget(
            user_id=user_id,
            category=category,
            limit=limit,
            period=period
        )
        await self.session.commit()
        return budget

    async def check_budget_alerts(self, user_id: int) -> List[str]:
        """Check for budget alerts."""
        alerts = []
        budgets = await self.repo.get_active_budgets(user_id)
        for budget in budgets:
            spent = await self.repo.get_spent_for_budget(budget.id)
            if spent > budget.limit:
                alerts.append(f"⚠️ Byudjet oshib ketdi: {budget.category}")
            elif spent > budget.limit * 0.8:
                alerts.append(f"⚠️ Byudjet tugamoqda: {budget.category}")
        return alerts

    async def recurring_transactions(self, user_id: int) -> None:
        """Process recurring transactions."""
        # This would typically be run by a cron job
        pass

    async def quick_transaction_parser(self, text: str) -> Dict[str, Any]:
        """Parse quick transaction string like '50000 taxi'."""
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            try:
                amount = float(parts[0])
                category = parts[1]
                return {"amount": amount, "category": category, "type": "expense"}
            except ValueError:
                pass
        raise ValueError("Noto'g'ri format. Masalan: 50000 taxi")
