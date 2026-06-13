from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.main_menu import main_menu_keyboard
from keyboards.inline import reminder_keyboard
from services.reminder_service import refresh_user_reminders

router = Router()


class ReminderStates(StatesGroup):
    choosing_type = State()
    entering_hour = State()
    entering_minute = State()


REMINDER_TYPES = {
    "breakfast": {"name": "🌅 Завтрак", "default_hour": 8, "default_minute": 0},
    "lunch": {"name": "☀️ Обед", "default_hour": 12, "default_minute": 30},
    "dinner": {"name": "🌙 Ужин", "default_hour": 18, "default_minute": 0},
    "water": {"name": "💧 Вода", "default_hour": 10, "default_minute": 0},
    "weigh_in": {"name": "⚖️ Взвешивание", "default_hour": 7, "default_minute": 30},
    "weekly_report": {"name": "📊 Еженедельный отчёт", "default_hour": 19, "default_minute": 0},
}


@router.message(F.text == "⏰ Напоминания")
async def reminders(message: Message):
    await db.record_button_click(message.from_user.id, "reminders")
    reminders_list = await db.get_reminders(message.from_user.id)

    if not reminders_list:
        for r_type, info in REMINDER_TYPES.items():
            await db.upsert_reminder(
                message.from_user.id, r_type,
                info["default_hour"], info["default_minute"], True
            )
        reminders_list = await db.get_reminders(message.from_user.id)

    text = "⏰ <b>Настройка напоминаний</b>\n\nНажмите на напоминание, чтобы включить/выключить:\n\n"

    kb = reminder_keyboard(reminders_list)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("toggle_reminder_"))
async def toggle_reminder(callback: CallbackQuery):
    reminder_type = callback.data.replace("toggle_reminder_", "")
    await db.toggle_reminder(callback.from_user.id, reminder_type)
    await refresh_user_reminders(callback.from_user.id)

    reminders_list = await db.get_reminders(callback.from_user.id)
    kb = reminder_keyboard(reminders_list)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer("Настройка обновлена!")
