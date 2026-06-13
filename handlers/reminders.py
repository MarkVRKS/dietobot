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
    choosing_reminder = State()
    entering_hour = State()
    entering_minute = State()


REMINDER_TYPES = {
    "breakfast": {"name": "🌅 Завтрак", "emoji": "🌅", "default_hour": 8, "default_minute": 0,
                  "description": "Напоминание о завтраке"},
    "lunch": {"name": "☀️ Обед", "emoji": "☀️", "default_hour": 12, "default_minute": 30,
              "description": "Напоминание об обеде"},
    "dinner": {"name": "🌙 Ужин", "emoji": "🌙", "default_hour": 18, "default_minute": 0,
               "description": "Напоминание об ужине"},
    "water": {"name": "💧 Вода", "emoji": "💧", "default_hour": 10, "default_minute": 0,
              "description": "Напоминание о питьевой воде"},
    "weigh_in": {"name": "⚖️ Взвешивание", "emoji": "⚖️", "default_hour": 7, "default_minute": 30,
                 "description": "Напоминание о взвешивании"},
    "weekly_report": {"name": "📊 Еженедельный отчёт", "emoji": "📊", "default_hour": 19, "default_minute": 0,
                      "description": "Еженедельный отчёт о прогрессе"},
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

    text = "⏰ <b>Настройка напоминаний</b>\n\n"
    text += "Нажмите на напоминание, чтобы включить/выключить.\n"
    text += "Нажмите ⏰ чтобы изменить время.\n\n"

    for r in reminders_list:
        r_type = r["reminder_type"]
        info = REMINDER_TYPES.get(r_type, {})
        name = info.get("name", r_type)
        status = "✅" if r["is_enabled"] else "❌"
        text += f"{status} {name} — {r['hour']:02d}:{r['minute']:02d}\n"

    kb = reminder_keyboard(reminders_list)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("toggle_reminder_"))
async def toggle_reminder(callback: CallbackQuery):
    reminder_type = callback.data.replace("toggle_reminder_", "")
    await db.toggle_reminder(callback.from_user.id, reminder_type)
    await refresh_user_reminders(callback.from_user.id)

    reminders_list = await db.get_reminders(callback.from_user.id)
    kb = reminder_keyboard(reminders_list)

    text = "⏰ <b>Напоминания обновлены!</b>\n\n"
    for r in reminders_list:
        r_type = r["reminder_type"]
        info = REMINDER_TYPES.get(r_type, {})
        name = info.get("name", r_type)
        status = "✅" if r["is_enabled"] else "❌"
        text += f"{status} {name} — {r['hour']:02d}:{r['minute']:02d}\n"

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer("Настройка обновлена!")


@router.callback_query(F.data.startswith("settime_reminder_"))
async def set_reminder_time(callback: CallbackQuery, state: FSMContext):
    reminder_type = callback.data.replace("settime_reminder_", "")
    info = REMINDER_TYPES.get(reminder_type, {})
    name = info.get("name", reminder_type)

    await state.update_data(reminder_type=reminder_type)
    await callback.message.answer(
        f"⏰ <b>Настройка времени для {name}</b>\n\n"
        f"Введите час (0-23):"
    )
    await state.set_state(ReminderStates.entering_hour)
    await callback.answer()


@router.message(ReminderStates.entering_hour)
async def enter_hour(message: Message, state: FSMContext):
    try:
        hour = int(message.text)
    except ValueError:
        await message.answer("Введите число от 0 до 23:")
        return

    if hour < 0 or hour > 23:
        await message.answer("Введите число от 0 до 23:")
        return

    await state.update_data(hour=hour)
    await message.answer("Введите минуты (0-59):")
    await state.set_state(ReminderStates.entering_minute)


@router.message(ReminderStates.entering_minute)
async def enter_minute(message: Message, state: FSMContext):
    try:
        minute = int(message.text)
    except ValueError:
        await message.answer("Введите число от 0 до 59:")
        return

    if minute < 0 or minute > 59:
        await message.answer("Введите число от 0 до 59:")
        return

    data = await state.get_data()
    reminder_type = data["reminder_type"]
    hour = data["hour"]
    info = REMINDER_TYPES.get(reminder_type, {})
    name = info.get("name", reminder_type)

    await db.upsert_reminder(message.from_user.id, reminder_type, hour, minute, True)
    await refresh_user_reminders(message.from_user.id)

    reminders_list = await db.get_reminders(message.from_user.id)
    kb = reminder_keyboard(reminders_list)

    text = f"✅ <b>Время для {name} обновлено!</b>\n\n"
    text += f"Новое время: <b>{hour:02d}:{minute:02d}</b>\n\n"
    text += "Все напоминания:\n"
    for r in reminders_list:
        r_type = r["reminder_type"]
        r_info = REMINDER_TYPES.get(r_type, {})
        r_name = r_info.get("name", r_type)
        status = "✅" if r["is_enabled"] else "❌"
        text += f"{status} {r_name} — {r['hour']:02d}:{r['minute']:02d}\n"

    await state.clear()
    await message.answer(text, reply_markup=kb)
