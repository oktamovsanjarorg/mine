"""
Guest and feedback handler.
Handles non-owner users by accepting inquiries and forwarding them to Sanjar (ID: 7537966029).
"""

import structlog
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.config import settings

logger = structlog.get_logger()
router = Router(name="guest")

OWNER_ID = 7537966029


class GuestReplyState(StatesGroup):
    waiting_for_reply = State()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in settings.bot_admin_ids or user_id in settings.admin_ids


@router.message(F.text.startswith("/start"), ~F.from_user.id.func(is_owner))
async def guest_start_handler(message: Message):
    """Start command for non-owner visitors."""
    text = (
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "Bu <b>Sanjarning</b> shaxsiy yordamchi boti.\n"
        "Agar Sanjarga biror muhim xabar, taklif yoki savolingiz bo'lsa, "
        "marhamat, shu yerga yozib qoldirishingiz mumkin.\n\n"
        "📩 <i>Xabaringiz zudlik bilan unga yetkaziladi.</i>"
    )
    await message.answer(text)


@router.message(~F.from_user.id.func(is_owner))
async def guest_message_handler(message: Message, bot: Bot):
    """Forward any message from non-owner to Sanjar."""
    user = message.from_user
    username_str = f" (@{user.username})" if user.username else ""
    sender_info = f"👤 <b>Kimdan:</b> {user.full_name}{username_str}\n🆔 <b>ID:</b> <code>{user.id}</code>"

    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Javob qaytarish", callback_data=f"guest_reply:{user.id}")]
    ])

    try:
        # Notify Sanjar
        await bot.send_message(
            chat_id=OWNER_ID,
            text=f"📬 <b>Yangi murojaat qabul qilindi!</b>\n\n{sender_info}\n\n👇 <i>Murojaat matni:</i>",
            reply_markup=reply_kb
        )
        # Send copy of original message (supports text, photo, audio, document, voice)
        await message.send_copy(chat_id=OWNER_ID)
        
        # Confirmation to guest
        await message.answer(
            "✅ <b>Xabaringiz Sanjarga yetkazildi!</b>\n\n"
            "Tez orada ko'rib chiqib, sizga javob qaytariladi. Rahmat!"
        )
        logger.info("Guest inquiry forwarded to owner", from_id=user.id)
    except Exception as e:
        logger.error("Failed to forward guest message", error=str(e))
        await message.answer("✅ Xabaringiz qabul qilindi. Tez orada javob beramiz.")


@router.callback_query(~F.from_user.id.func(is_owner))
async def guest_callback_handler(callback: CallbackQuery):
    """Deny callback interactions for non-owners."""
    await callback.answer("⚠️ Ushbu imkoniyat faqat bot egasi uchun mavjud.", show_alert=True)


# ==================== OWNER REPLYING TO GUEST ====================

@router.callback_query(F.data.startswith("guest_reply:"), F.from_user.id.func(is_owner))
async def owner_start_reply(callback: CallbackQuery, state: FSMContext):
    """Owner clicks 'Javob qaytarish' button."""
    guest_id = int(callback.data.split(":")[1])
    await state.set_state(GuestReplyState.waiting_for_reply)
    await state.update_data(target_guest_id=guest_id)
    
    await callback.message.answer(
        f"✍️ <code>{guest_id}</code> raqamli foydalanuvchiga yuboriladigan javob xabaringizni yozing:"
    )
    await callback.answer()


@router.message(GuestReplyState.waiting_for_reply, F.from_user.id.func(is_owner))
async def owner_send_reply(message: Message, state: FSMContext, bot: Bot):
    """Send owner's reply back to the guest user."""
    data = await state.get_data()
    guest_id = data.get("target_guest_id")
    await state.clear()

    if not guest_id:
        await message.answer("❌ Foydalanuvchi ID si topilmadi.")
        return

    try:
        header = "💬 <b>Sanjardan sizga javob keldi:</b>\n\n"
        if message.text:
            await bot.send_message(chat_id=guest_id, text=header + message.text)
        else:
            await bot.send_message(chat_id=guest_id, text=header)
            await message.send_copy(chat_id=guest_id)
            
        await message.answer(f"✅ Javob <code>{guest_id}</code> ga muvaffaqiyatli yuborildi!")
    except Exception as e:
        logger.error("Failed to deliver reply to guest", guest_id=guest_id, error=str(e))
        await message.answer(f"❌ Xatolik: Javob yuborilmadi ({e})")
