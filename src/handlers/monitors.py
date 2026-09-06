import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.monitor import MonitorService
from src.states.monitor import MonitorStates

logger = structlog.get_logger(__name__)
router = Router(name="monitors_router")


def build_monitors_markup(monitors) -> InlineKeyboardMarkup:
    keyboard = []
    for m in monitors:
        status_icon = "🟢" if m.is_active else "🔴"
        row = [
            InlineKeyboardButton(text=f"{status_icon} #{m.id} {m.name[:15]}", callback_data=f"mon_check:{m.id}"),
            InlineKeyboardButton(text="🔄 Tekshirish", callback_data=f"mon_check:{m.id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"mon_del:{m.id}"),
        ]
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="➕ Yangi monitor qo'shish", callback_data="mon_add_btn")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("monitors"))
@router.message(F.text == "📈 Monitorlar")
async def monitors_menu(message: Message, session: AsyncSession, user: User) -> None:
    """List website monitors."""
    service = MonitorService(session)
    monitors = await service.get_user_monitors(user.id)
    if not monitors:
        await message.answer(
            "📈 <b>Veb-sayt monitorlari bo'sh!</b>\n\n"
            "Saytni monitoring qilish uchun:\n"
            "<code>/addmonitor https://example.com Mening saytim</code>\n"
            "yoki quyidagi tugmani bosing:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="➕ Yangi monitor qo'shish", callback_data="mon_add_btn")
            ]]),
            parse_mode="HTML"
        )
        return

    lines = ["📈 <b>Sizning veb-sayt monitorlaringiz:</b>\n"]
    for i, m in enumerate(monitors, 1):
        status = "Faol 🟢" if m.is_active else "Nofaol 🔴"
        last_val = (m.last_value or "Hali tekshirilmadi")[:45]
        lines.append(f"{i}. <b>{m.name}</b> ({status})\n   🔗 <code>{m.url}</code>\n   ℹ️ <i>{last_val}</i>")

    markup = build_monitors_markup(monitors)
    await message.answer("\n".join(lines), reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


@router.callback_query(F.data == "mon_add_btn")
async def mon_add_btn_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("🌐 Kuzatish uchun sayt URL manzilini kiriting (masalan, <code>https://kun.uz</code>):", parse_mode="HTML")
    await state.set_state(MonitorStates.waiting_url)
    await callback.answer()


@router.message(Command("addmonitor"))
async def add_monitor(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    """Start monitor creation or add via arguments."""
    args = message.text.split(maxsplit=2)
    if len(args) >= 2:
        url = args[1].strip()
        name = args[2].strip() if len(args) > 2 else url.replace("https://", "").replace("http://", "").split("/")[0]
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        service = MonitorService(session)
        msg_wait = await message.answer("🔄 Sayt birinchi marta tekshirilmoqda...")
        try:
            monitor = await service.create_monitor(user_id=user.id, url=url, name=name)
            await msg_wait.edit_text(
                f"✅ <b>Monitor muvaffaqiyatli qo'shildi!</b>\n\n"
                f"🏷 <b>Nomi:</b> {monitor.name}\n"
                f"🔗 <b>URL:</b> <code>{monitor.url}</code>\n"
                f"📊 <b>Boshlang'ich qiymat:</b> {monitor.last_value or 'Noma`lum'}",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error("Monitor qo'shishda xato", error=str(e))
            await msg_wait.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")
        return

    await message.answer("🌐 Kuzatish uchun veb-sayt URL manzilini kiriting:")
    await state.set_state(MonitorStates.waiting_url)


@router.message(MonitorStates.waiting_url, F.text)
async def monitor_url(message: Message, state: FSMContext) -> None:
    """Handle monitor URL."""
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    await state.update_data(url=url)
    default_name = url.replace("https://", "").replace("http://", "").split("/")[0]
    await message.answer(f"🏷 Monitor uchun nom kiriting (yoki <code>{default_name}</code> deb qoldirish uchun '-' yuboring):", parse_mode="HTML")
    await state.set_state(MonitorStates.waiting_name)


@router.message(MonitorStates.waiting_name, F.text)
async def monitor_name(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    """Save monitor from state."""
    data = await state.get_data()
    url = data["url"]
    name = message.text.strip()
    if name == "-":
        name = url.replace("https://", "").replace("http://", "").split("/")[0]

    await state.clear()
    msg_wait = await message.answer("🔄 Sayt dastlabki tekshiruvdan o'tkazilmoqda...")
    service = MonitorService(session)
    try:
        monitor = await service.create_monitor(user_id=user.id, url=url, name=name)
        await msg_wait.edit_text(
            f"✅ <b>Monitor muvaffaqiyatli qo'shildi!</b>\n\n"
            f"🏷 <b>Nomi:</b> {monitor.name}\n"
            f"🔗 <b>URL:</b> <code>{monitor.url}</code>\n"
            f"📊 <b>Holat:</b> {monitor.last_value or 'Kuzatuv faol'}",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error("Monitor qo'shishda xato", error=str(e))
        await msg_wait.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")


@router.message(Command("checkmonitor"))
async def check_monitor(message: Message, session: AsyncSession, user: User) -> None:
    """Manual trigger check."""
    service = MonitorService(session)
    monitors = await service.get_user_monitors(user.id)
    if not monitors:
        await message.answer("📈 Sizda hali faol monitorlar yo'q. /addmonitor orqali qo'shing.")
        return

    msg_wait = await message.answer("🔄 Barcha monitorlar tekshirilmoqda...")
    report = ["🔍 <b>Monitorlar tekshiruvi natijalari:</b>\n"]
    for m in monitors:
        changed, detail = await service.check_monitor(m.id)
        status = "⚡️ O'ZGARISH!" if changed else "✅ O'zgarishsiz"
        report.append(f"• <b>{m.name}</b>: {status}\n  <i>{detail}</i>")

    await msg_wait.edit_text("\n".join(report), parse_mode="HTML")


@router.callback_query(F.data.startswith("mon_check:"))
async def monitor_check_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    """Check a specific monitor."""
    mon_id = int(callback.data.split(":")[1])
    service = MonitorService(session)
    changed, detail = await service.check_monitor(mon_id)
    alert = "⚡️ Sayt tarkibida o'zgarish bor!" if changed else "✅ O'zgarish aniqlanmadi"
    await callback.answer(alert, show_alert=True)


@router.callback_query(F.data.startswith("mon_del:"))
async def monitor_del_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    """Delete monitor."""
    mon_id = int(callback.data.split(":")[1])
    service = MonitorService(session)
    await service.delete_monitor(mon_id)
    await callback.answer("🗑 Monitor o'chirildi!")

    monitors = await service.get_user_monitors(user.id)
    if not monitors:
        await callback.message.edit_text("📈 <b>Barcha monitorlar o'chirildi.</b>", parse_mode="HTML")
        return

    lines = ["📈 <b>Sizning veb-sayt monitorlaringiz:</b>\n"]
    for i, m in enumerate(monitors, 1):
        status = "Faol 🟢" if m.is_active else "Nofaol 🔴"
        last_val = (m.last_value or "Hali tekshirilmadi")[:45]
        lines.append(f"{i}. <b>{m.name}</b> ({status})\n   🔗 <code>{m.url}</code>\n   ℹ️ <i>{last_val}</i>")

    markup = build_monitors_markup(monitors)
    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        pass

