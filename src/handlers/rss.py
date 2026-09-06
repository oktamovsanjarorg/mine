import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.rss import RSSService

logger = structlog.get_logger(__name__)
router = Router(name="rss_router")


class RSSCreateState(StatesGroup):
    waiting_url = State()


def build_rss_markup(feeds) -> InlineKeyboardMarkup:
    keyboard = []
    for f in feeds:
        row = [
            InlineKeyboardButton(text=f"📰 #{f.id} {f.title[:20]}", callback_data=f"rss_info:{f.id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"rss_del:{f.id}"),
        ]
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton(text="⚡️ Yangiliklarni o'qish", callback_data="rss_news_btn"),
        InlineKeyboardButton(text="➕ RSS qo'shish", callback_data="rss_add_btn"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("rss"))
@router.message(F.text == "📰 RSS lentalar")
async def rss_menu(message: Message, session: AsyncSession, user: User) -> None:
    """RSS feed menu."""
    service = RSSService(session)
    feeds = await service.get_user_feeds(user.id)
    if not feeds:
        await message.answer(
            "📰 <b>Sizda hozircha RSS kanallar mavjud emas!</b>\n\n"
            "Kanal qo'shish uchun:\n"
            "<code>/addrss https://kun.uz/news/rss</code>\n"
            "yoki quyidagi tugmani bosing:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="➕ RSS qo'shish", callback_data="rss_add_btn")
            ]]),
            parse_mode="HTML"
        )
        return

    lines = ["📰 <b>Sizning ulangan RSS kanallaringiz:</b>\n"]
    for i, f in enumerate(feeds, 1):
        lines.append(f"{i}. <b>{f.title}</b>\n   🔗 <code>{f.url}</code>")

    lines.append("\n💡 Yangi xabarlarni ko'rish uchun: /news")
    markup = build_rss_markup(feeds)
    await message.answer("\n".join(lines), reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


@router.callback_query(F.data == "rss_add_btn")
async def rss_add_btn_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("🌐 RSS lentasi URL manzilini yuboring (masalan: <code>https://kun.uz/news/rss</code>):", parse_mode="HTML")
    await state.set_state(RSSCreateState.waiting_url)
    await callback.answer()


@router.message(Command("addrss"))
async def add_rss(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    """Add RSS feed."""
    args = message.text.split(maxsplit=1)
    if len(args) >= 2:
        url = args[1].strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        msg_wait = await message.answer("🔄 RSS lentasi tekshirilmoqda va ulanmoqda...")
        service = RSSService(session)
        try:
            feed = await service.add_feed(user_id=user.id, url=url)
            await msg_wait.edit_text(
                f"✅ <b>RSS kanal muvaffaqiyatli qo'shildi!</b>\n\n"
                f"📰 <b>Nomi:</b> {feed.title}\n"
                f"🔗 <b>URL:</b> <code>{feed.url}</code>\n"
                f"So'nggi yangiliklarni o'qish uchun /news buyrug'ini bosing.",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error("RSS add failed", error=str(e))
            await msg_wait.edit_text(f"❌ RSS lentasini qo'shib bo'lmadi: {str(e)}")
        return

    await message.answer("🌐 RSS havolasini kiriting (masalan: <code>/addrss https://kun.uz/news/rss</code>):", parse_mode="HTML")
    await state.set_state(RSSCreateState.waiting_url)


@router.message(RSSCreateState.waiting_url, F.text)
async def rss_url_input(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    await state.clear()
    msg_wait = await message.answer("🔄 RSS lentasi tahlil qilinmoqda...")
    service = RSSService(session)
    try:
        feed = await service.add_feed(user_id=user.id, url=url)
        await msg_wait.edit_text(
            f"✅ <b>RSS kanal muvaffaqiyatli qo'shildi!</b>\n\n"
            f"📰 <b>Nomi:</b> {feed.title}\n"
            f"🔗 <b>URL:</b> <code>{feed.url}</code>\n"
            f"So'nggi yangiliklarni o'qish uchun /news buyrug'ini bosing.",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error("RSS add failed", error=str(e))
        await msg_wait.edit_text(f"❌ RSS lentasini qo'shib bo'lmadi: {str(e)}")


@router.message(Command("news"))
@router.callback_query(F.data == "rss_news_btn")
async def read_news(event: Message | CallbackQuery, session: AsyncSession, user: User) -> None:
    """Read unread news."""
    message = event if isinstance(event, Message) else event.message
    if isinstance(event, CallbackQuery):
        await event.answer()

    service = RSSService(session)
    # Check feeds first
    feeds = await service.get_user_feeds(user.id)
    if not feeds:
        await message.answer("📰 Sizda ulangan RSS kanallar yo'q. /addrss orqali qo'shing.")
        return

    for f in feeds:
        await service.check_feed(f.id)

    items = await service.get_unread_items(user.id, limit=7)
    if not items:
        await message.answer("📰 <b>Barcha yangiliklar o'qib bo'lingan!</b> Yangi xabarlar yo'q.", parse_mode="HTML")
        return

    lines = ["📰 <b>So'nggi yangiliklar:</b>\n"]
    keyboard = []
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. <b><a href='{item.link}'>{item.title}</a></b>")
        keyboard.append([
            InlineKeyboardButton(text=f"📖 #{item.id} O'qish", url=item.link),
            InlineKeyboardButton(text="✔️ O'qildi", callback_data=f"rss_read:{item.id}")
        ])

    keyboard.append([InlineKeyboardButton(text="🔄 Yangilash", callback_data="rss_news_btn")])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("\n".join(lines), reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


@router.callback_query(F.data.startswith("rss_read:"))
async def rss_mark_read_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    item_id = int(callback.data.split(":")[1])
    service = RSSService(session)
    await service.mark_read(item_id)
    await callback.answer("✔️ O'qilgan deb belgilandi!")


@router.callback_query(F.data.startswith("rss_del:"))
async def rss_delete_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    feed_id = int(callback.data.split(":")[1])
    service = RSSService(session)
    await service.delete_feed(feed_id)
    await callback.answer("🗑 RSS kanal o'chirildi!")

    feeds = await service.get_user_feeds(user.id)
    if not feeds:
        await callback.message.edit_text("📰 <b>Barcha RSS kanallar o'chirildi.</b>", parse_mode="HTML")
        return

    lines = ["📰 <b>Sizning ulangan RSS kanallaringiz:</b>\n"]
    for i, f in enumerate(feeds, 1):
        lines.append(f"{i}. <b>{f.title}</b>\n   🔗 <code>{f.url}</code>")

    markup = build_rss_markup(feeds)
    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        pass

