import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="monitors_router")

class MonitorCreate(StatesGroup):
    url = State()
    interval = State()

@router.message(Command("monitors"))
async def monitors_menu(message: Message) -> None:
    """List website monitors."""
    await message.answer("📈 Veb-sayt monitorlari:\nHech qanday sayt kuzatilmayapti.")

@router.message(Command("addmonitor"))
async def add_monitor(message: Message, state: FSMContext) -> None:
    """Start monitor creation."""
    await message.answer("Kuzatish uchun sayt URL manzilini kiriting:")
    await state.set_state(MonitorCreate.url)

@router.message(MonitorCreate.url, F.text)
async def monitor_url(message: Message, state: FSMContext) -> None:
    """Handle monitor URL."""
    await state.update_data(url=message.text)
    await message.answer("Tekshirish oralig'ini kiriting (daqiqalarda):")
    await state.set_state(MonitorCreate.interval)
    
@router.message(MonitorCreate.interval, F.text)
async def monitor_interval(message: Message, state: FSMContext) -> None:
    """Save monitor."""
    await state.clear()
    await message.answer("✅ Monitor qo'shildi. O'zgarishlar haqida xabar beramiz!")

@router.message(Command("checkmonitor"))
async def check_monitor(message: Message) -> None:
    """Manual trigger check."""
    await message.answer("🔄 Barcha monitorlar tekshirilmoqda...")
