import pytest
from src.services.finance import FinanceService

@pytest.fixture
def finance_service(async_session):
    return FinanceService(async_session)

@pytest.mark.asyncio
async def test_add_income(finance_service, test_user):
    tx = await finance_service.add_income(
        user_id=test_user.id,
        amount=1000000,
        category="Oylik",
        description="Maosh"
    )
    assert float(tx.amount) == 1000000
    assert str(tx.type) == "income"

@pytest.mark.asyncio
async def test_add_expense(finance_service, test_user):
    tx = await finance_service.add_expense(
        user_id=test_user.id,
        amount=50000,
        category="Transport",
        description="Taksim"
    )
    assert float(tx.amount) == 50000
    assert str(tx.type) == "expense"

@pytest.mark.asyncio
async def test_balance_calculation(finance_service, test_user):
    await finance_service.add_income(test_user.id, 1000000, "Oylik")
    await finance_service.add_expense(test_user.id, 200000, "Oziq-ovqat")
    await finance_service.add_expense(test_user.id, 50000, "Transport")
    
    balance = await finance_service.get_balance(test_user.id)
    assert balance == 750000

@pytest.mark.asyncio
async def test_quick_transaction_parser(finance_service, test_user):
    tx = await finance_service.parse_and_create(test_user.id, "50000 tushlik +")
    assert float(tx.amount) == 50000
    assert str(tx.type) == "income"
    assert "tushlik" in tx.description
    
    tx2 = await finance_service.parse_and_create(test_user.id, "25000 taksi -")
    assert float(tx2.amount) == 25000
    assert str(tx2.type) == "expense"
    assert "taksi" in tx2.description
