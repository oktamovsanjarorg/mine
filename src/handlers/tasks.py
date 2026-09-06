"""
Tasks Handler - Full CRUD and Interactive Workflow.
"""

import structlog
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.task import TaskService
from src.models.user import User
from src.models.task import TaskStatus, TaskPriority
from src.core.utils.datetime_utils import parse_datetime

logger = structlog.get_logger(__name__)
router = Router(name="tasks_router")


class TaskCreate(StatesGroup):
    title = State()
    description = State()
    priority = State()
    due_date = State()


def build_task_list_markup(tasks) -> InlineKeyboardMarkup:
    """Build interactive inline keyboard for tasks."""
    keyboard = []
    for t in tasks:
        status_btn = "✅" if not t.is_completed else "↩️"
        row = [
            InlineKeyboardButton(text=f"{status_btn} #{t.id}", callback_data=f"task_toggle:{t.id}"),
            InlineKeyboardButton(text=f"🗑 #{t.id}", callback_data=f"task_del:{t.id}"),
        ]
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(text="➕ Yangi vazifa", callback_data="task_add_btn"),
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="task_refresh_btn"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_task_text(tasks) -> str:
    if not tasks:
        return (
            "📋 <b>Sizda hozircha hech qanday vazifa yo'q!</b>\n\n"
            "Yangi vazifa qo'shish uchun pastdagi tugmani bosing yoki /addtask buyrug'ini yuboring."
        )

    lines = ["📋 <b>Sizning vazifalaringiz ro'yxati:</b>\n"]
    for i, t in enumerate(tasks, 1):
        status_icon = "✅" if t.is_completed else "⏳"
        priority_icon = "🔴" if str(t.priority) in ("high", "highest", "4", "5") else "🟡"
        due_str = f" <i>(Muddat: {t.due_date.strftime('%d.%m %H:%M')})</i>" if t.due_date else ""
        lines.append(f"{i}. {status_icon} {priority_icon} <b>#{t.id}: {t.title}</b>{due_str}")
        if t.description:
            lines.append(f"   ▫️ <i>{t.description}</i>")
    return "\n".join(lines)


@router.message(Command("tasks"))
@router.message(F.text == "📋 Vazifalar")
async def list_tasks_handler(message: Message, session: AsyncSession, user: User) -> None:
    """List all user tasks."""
    service = TaskService(session)
    tasks = await service.get_tasks(user.id, limit=15)
    text = format_task_text(tasks)
    markup = build_task_list_markup(tasks)
    await message.answer(text, reply_markup=markup, parse_mode="HTML")


@router.message(Command("addtask"))
async def add_task_start(message: Message, state: FSMContext) -> None:
    """Start FSM for creating a task."""
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        # Quick inline add: /addtask Kitob o'qish
        title = args[1].strip()
        await state.update_data(title=title)
        await message.answer("📄 Vazifa tavsifini kiriting (yoki /skip):")
        await state.set_state(TaskCreate.description)
        return

    await message.answer("📝 <b>Yangi vazifa nomini kiriting:</b>", parse_mode="HTML")
    await state.set_state(TaskCreate.title)


@router.callback_query(F.data == "task_add_btn")
async def add_task_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("📝 <b>Yangi vazifa nomini kiriting:</b>", parse_mode="HTML")
    await state.set_state(TaskCreate.title)
    await callback.answer()


@router.callback_query(F.data == "task_refresh_btn")
async def refresh_tasks_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    service = TaskService(session)
    tasks = await service.get_tasks(user.id, limit=15)
    text = format_task_text(tasks)
    markup = build_task_list_markup(tasks)
    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("Yangilandi!")


@router.message(TaskCreate.title, F.text)
async def add_task_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await message.answer("📄 Vazifa tafsilotini/tavsifini kiriting (yoki /skip):")
    await state.set_state(TaskCreate.description)


@router.message(TaskCreate.description, F.text)
async def add_task_desc(message: Message, state: FSMContext) -> None:
    desc = None if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(description=desc)

    priority_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Yuqori", callback_data="task_prio:high"),
            InlineKeyboardButton(text="🟡 O'rta", callback_data="task_prio:medium"),
            InlineKeyboardButton(text="🟢 Past", callback_data="task_prio:low"),
        ]
    ])
    await message.answer("⚡ <b>Ustuvorlik darajasini tanlang:</b>", reply_markup=priority_kb, parse_mode="HTML")
    await state.set_state(TaskCreate.priority)


@router.callback_query(TaskCreate.priority, F.data.startswith("task_prio:"))
async def add_task_prio(callback: CallbackQuery, state: FSMContext) -> None:
    prio = callback.data.split(":")[1]
    await state.update_data(priority=prio)
    await callback.message.answer("📅 <b>Muddatni kiriting</b> (masalan: <code>ertaga 18:00</code>, <code>2h</code>, <code>2026-10-01</code> yoki /skip):", parse_mode="HTML")
    await state.set_state(TaskCreate.due_date)
    await callback.answer()


@router.message(TaskCreate.due_date, F.text)
async def add_task_finish(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    data = await state.get_data()
    await state.clear()

    due_date = None
    if message.text.strip() != "/skip":
        due_date = parse_datetime(message.text.strip())

    service = TaskService(session)
    task = await service.create_task(
        user_id=user.id,
        title=data["title"],
        description=data.get("description"),
        due_date=due_date
    )

    due_str = f"\n📅 Muddat: {task.due_date.strftime('%Y-%m-%d %H:%M')}" if task.due_date else ""
    await message.answer(
        f"✅ <b>Vazifa muvaffaqiyatli saqlandi!</b>\n\n"
        f"🆔 #{task.id}: <b>{task.title}</b>\n"
        f"⚡ Ustuvorlik: {data.get('priority', 'medium')}"
        f"{due_str}",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("task_toggle:"))
async def toggle_task_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    task_id = int(callback.data.split(":")[1])
    service = TaskService(session)
    task = await service.repo.get_by_id(task_id)
    if task and task.user_id == user.id:
        if task.is_completed:
            await service.update_task(task_id, status=TaskStatus.TODO, completed_at=None)
            await callback.answer("Vazifa qayta ochildi!")
        else:
            await service.complete_task(task_id)
            await callback.answer("✅ Bajarildi deb belgilandi!")
        
        tasks = await service.get_tasks(user.id, limit=15)
        text = format_task_text(tasks)
        markup = build_task_list_markup(tasks)
        try:
            await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        except Exception:
            pass
    else:
        await callback.answer("Vazifa topilmadi!", show_alert=True)


@router.callback_query(F.data.startswith("task_del:"))
async def delete_task_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    task_id = int(callback.data.split(":")[1])
    service = TaskService(session)
    task = await service.repo.get_by_id(task_id)
    if task and task.user_id == user.id:
        await service.delete_task(task_id)
        await callback.answer("🗑 Vazifa o'chirildi!")
        tasks = await service.get_tasks(user.id, limit=15)
        text = format_task_text(tasks)
        markup = build_task_list_markup(tasks)
        try:
            await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        except Exception:
            pass
    else:
        await callback.answer("Vazifa topilmadi!", show_alert=True)


@router.message(Command("donetask"))
async def done_task_cmd(message: Message, session: AsyncSession, user: User) -> None:
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("ℹ️ Foydalanish: <code>/donetask [vazifa_id]</code>", parse_mode="HTML")
        return

    task_id = int(args[1])
    service = TaskService(session)
    task = await service.repo.get_by_id(task_id)
    if task and task.user_id == user.id:
        await service.complete_task(task_id)
        await message.answer(f"✅ #{task.id} <b>{task.title}</b> bajarildi deb belgilandi!", parse_mode="HTML")
    else:
        await message.answer("❌ Vazifa topilmadi.")
