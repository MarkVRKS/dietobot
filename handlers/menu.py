from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.main_menu import main_menu_keyboard
from keyboards.inline import menu_generation_keyboard, day_view_keyboard
from services.menu_generator import generate_weekly_menu, format_menu_text
from services.shopping_list import generate_shopping_list
from datetime import date, timedelta
import json

router = Router()


class MenuStates(StatesGroup):
    waiting_for_menu = State()


@router.message(F.text == "📋 Меню на неделю")
async def weekly_menu(message: Message):
    await db.record_button_click(message.from_user.id, "weekly_menu")
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("gender"):
        await message.answer("Сначала заполните профиль через /start")
        return

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    existing = await db.get_weekly_menu(message.from_user.id, week_start)
    if existing:
        menu = json.loads(existing)
        text = format_menu_text(menu, 0)
        await message.answer(text, reply_markup=menu_generation_keyboard())
    else:
        await generate_new_menu(message, user)


async def generate_new_menu(message: Message, user: dict):
    profile = {
        "daily_calories": user.get("daily_calories", 2000),
        "deficit_calories": user.get("daily_calories", 2000),
        "daily_protein": user.get("daily_protein", 100),
        "daily_fat": user.get("daily_fat", 70),
        "daily_carbs": user.get("daily_carbs", 200),
        "restrictions": user.get("restrictions", ""),
    }

    menu = generate_weekly_menu(profile)

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    await db.save_weekly_menu(message.from_user.id, week_start, json.dumps(menu, ensure_ascii=False))

    text = format_menu_text(menu, 0)
    await message.answer("✅ Меню на неделю сгенерировано!\n\n" + text,
                        reply_markup=menu_generation_keyboard())


@router.callback_query(F.data == "generate_menu")
async def regenerate_menu(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user or not user.get("gender"):
        await callback.message.answer("Сначала заполните профиль.")
        await callback.answer()
        return

    await callback.answer("Генерирую новое меню...")

    profile = {
        "daily_calories": user.get("daily_calories", 2000),
        "deficit_calories": user.get("daily_calories", 2000),
        "daily_protein": user.get("daily_protein", 100),
        "daily_fat": user.get("daily_fat", 70),
        "daily_carbs": user.get("daily_carbs", 200),
        "restrictions": user.get("restrictions", ""),
    }

    menu = generate_weekly_menu(profile)

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    await db.save_weekly_menu(callback.from_user.id, week_start, json.dumps(menu, ensure_ascii=False))

    text = format_menu_text(menu, 0)
    await callback.message.edit_text(text, reply_markup=menu_generation_keyboard())


@router.callback_query(F.data.startswith("day_"))
async def show_day(callback: CallbackQuery):
    day_index = int(callback.data.split("_")[1])
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    menu_json = await db.get_weekly_menu(callback.from_user.id, week_start)
    if not menu_json:
        await callback.message.answer("Меню не найдено. Сгенерируйте заново.")
        await callback.answer()
        return

    menu = json.loads(menu_json)
    text = format_menu_text(menu, day_index)
    await callback.message.edit_text(text, reply_markup=day_view_keyboard(day_index))
    await callback.answer()


@router.callback_query(F.data == "shopping_list")
async def shopping_list(callback: CallbackQuery):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    menu_json = await db.get_weekly_menu(callback.from_user.id, week_start)
    if not menu_json:
        await callback.message.answer("Сначала сгенерируйте меню на неделю.")
        await callback.answer()
        return

    menu = json.loads(menu_json)
    text = generate_shopping_list(menu)
    await callback.message.answer(text)
    await callback.answer()
