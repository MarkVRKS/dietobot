from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database import db
from keyboards.main_menu import main_menu_keyboard, water_keyboard
from keyboards.inline import water_inline_keyboard
from services.calorie_calculator import get_water_goal
from services.weight_service import create_water_chart

router = Router()


@router.message(F.text == "💧 Вода")
async def water_tracker(message: Message):
    await db.record_button_click(message.from_user.id, "water")
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("gender"):
        await message.answer("Сначала заполните профиль через /start")
        return

    current = await db.get_water_today(message.from_user.id)
    weight = user.get("current_weight", 70)
    goal = get_water_goal(weight)
    progress = min(current / goal * 100, 100) if goal > 0 else 0

    bar_filled = int(progress / 5)
    bar_empty = 20 - bar_filled
    bar = "█" * bar_filled + "░" * bar_empty

    text = (
        f"💧 <b>Водный трекер</b>\n\n"
        f"Сегодня: <b>{current}</b> мл / <b>{goal}</b> мл\n"
        f"[{bar}] {progress:.0f}%\n\n"
        f"Цель рассчитана: {weight} кг × 30 мл = {goal} мл\n\n"
        f"Нажмите кнопку, чтобы добавить воду:"
    )

    await message.answer(text, reply_markup=water_keyboard())


@router.message(F.text.regexp(r"💧 \d+"))
async def add_water(message: Message):
    amount_map = {
        "💧 250 мл": 250,
        "💧 500 мл": 500,
        "💧 750 мл": 750,
        "💧 1 литр": 1000,
    }
    amount = amount_map.get(message.text, 0)
    if amount == 0:
        return

    await db.add_water_entry(message.from_user.id, amount)
    user = await db.get_user(message.from_user.id)
    current = await db.get_water_today(message.from_user.id)
    weight = user.get("current_weight", 70) if user else 70
    goal = get_water_goal(weight)
    progress = min(current / goal * 100, 100) if goal > 0 else 0

    bar_filled = int(progress / 5)
    bar_empty = 20 - bar_filled
    bar = "█" * bar_filled + "░" * bar_empty

    text = (
        f"✅ Добавлено {amount} мл\n\n"
        f"Сегодня: <b>{current}</b> мл / <b>{goal}</b> мл\n"
        f"[{bar}] {progress:.0f}%"
    )

    if current >= goal:
        text += "\n\n🎉 Цель достигнута! Отличная работа!"

    await message.answer(text, reply_markup=water_keyboard())
