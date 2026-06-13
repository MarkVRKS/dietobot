from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.main_menu import main_menu_keyboard, gender_keyboard, activity_keyboard, diet_keyboard
from keyboards.inline import profile_keyboard, settings_keyboard
from services.calorie_calculator import calculate_full_profile

router = Router()


class EditProfile(StatesGroup):
    gender = State()
    age = State()
    height = State()
    current_weight = State()
    target_weight = State()
    activity_level = State()
    diet_type = State()


@router.message(F.text == "⚙️ Настройки")
async def settings(message: Message):
    await db.record_button_click(message.from_user.id, "settings")
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("gender"):
        await message.answer("Сначала заполните профиль через /start")
        return

    gender_text = "Мужской" if user["gender"] == "male" else "Женский"
    activity_names = {
        "sedentary": "Малоподвижный",
        "light": "Лёгкая активность",
        "moderate": "Умеренная активность",
        "active": "Высокая активность",
        "very_active": "Очень высокая",
    }
    diet_names = {
        "balanced": "Сбалансированное",
        "high_protein": "Высокобелковое",
        "low_carb": "Низкоуглеводное",
        "keto": "Кетогенное",
        "vegetarian": "Вегетарианское",
    }

    text = (
        f"👤 <b>Ваш профиль:</b>\n\n"
        f"Пол: {gender_text}\n"
        f"Возраст: {user.get('age', '—')} лет\n"
        f"Рост: {user.get('height', '—')} см\n"
        f"Вес: {user.get('current_weight', '—')} кг\n"
        f"Цель: {user.get('target_weight', '—')} кг\n"
        f"Активность: {activity_names.get(user.get('activity_level', ''), '—')}\n"
        f"Питание: {diet_names.get(user.get('diet_type', ''), '—')}\n\n"
        f"📊 <b>Расчёт:</b>\n"
        f"🔥 BMR: {user.get('bmr', '—')} ккал\n"
        f"📊 Норма: {user.get('daily_calories', '—')} ккал\n"
        f"🥩 Белки: {user.get('daily_protein', '—')}г\n"
        f"🧈 Жиры: {user.get('daily_fat', '—')}г\n"
        f"🍞 Углеводы: {user.get('daily_carbs', '—')}г\n"
    )

    await message.answer(text, reply_markup=settings_keyboard())


@router.callback_query(F.data == "edit_profile")
async def edit_profile_callback(callback):
    await callback.message.answer(
        "👤 Укажите ваш <b>пол</b>:",
        reply_markup=gender_keyboard()
    )
    await callback.answer()
    state = callback.bot.get("state") if hasattr(callback.bot, "get_state") else None


@router.callback_query(F.data == "my_profile")
async def my_profile_callback(callback):
    user = await db.get_user(callback.from_user.id)
    if not user or not user.get("gender"):
        await callback.message.answer("Профиль не заполнен. Используйте /start")
        await callback.answer()
        return

    gender_text = "Мужской" if user["gender"] == "male" else "Женский"
    text = (
        f"👤 <b>Ваш профиль:</b>\n\n"
        f"Пол: {gender_text}\n"
        f"Возраст: {user.get('age', '—')} лет\n"
        f"Рост: {user.get('height', '—')} см\n"
        f"Вес: {user.get('current_weight', '—')} кг\n"
        f"Цель: {user.get('target_weight', '—')} кг\n"
        f"\n📊 Расчёт:\n"
        f"🔥 BMR: {user.get('bmr', '—')} ккал\n"
        f"📊 Норма: {user.get('daily_calories', '—')} ккал\n"
    )
    await callback.message.answer(text, reply_markup=profile_keyboard())
    await callback.answer()


@router.callback_query(F.data == "recalc_calories")
async def recalc_callback(callback):
    user = await db.get_user(callback.from_user.id)
    if not user or not user.get("gender"):
        await callback.message.answer("Сначала заполните профиль.")
        await callback.answer()
        return

    profile = calculate_full_profile(
        gender=user["gender"],
        age=user["age"],
        height=user["height"],
        current_weight=user["current_weight"],
        target_weight=user["target_weight"],
        activity_level=user["activity_level"],
        diet_type=user["diet_type"],
    )

    await db.update_user(
        callback.from_user.id,
        bmr=profile["bmr"],
        daily_calories=profile["deficit_calories"],
        daily_protein=profile["daily_protein"],
        daily_fat=profile["daily_fat"],
        daily_carbs=profile["daily_carbs"],
    )

    text = (
        f"✅ <b>Калории пересчитаны!</b>\n\n"
        f"🔥 BMR: {profile['bmr']} ккал\n"
        f"📊 Суточная норма: {profile['daily_calories']} ккал\n"
        f"📉 Дефицит: {profile['deficit_calories']} ккал\n\n"
        f"🥩 Белки: {profile['daily_protein']}г\n"
        f"🧈 Жиры: {profile['daily_fat']}г\n"
        f"🍞 Углеводы: {profile['daily_carbs']}г"
    )
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "change_target")
async def change_target_callback(callback):
    await callback.message.answer("🎯 Введите новый <b>целевой вес</b> (кг):")
    await callback.answer()
    # We'll handle the text in a generic handler


@router.callback_query(F.data == "change_diet")
async def change_diet_callback(callback):
    await callback.message.answer("🥗 Выберите новый тип <b>питания</b>:",
                                   reply_markup=diet_keyboard())
    await callback.answer()


@router.callback_query(F.data == "change_activity")
async def change_activity_callback(callback):
    await callback.message.answer("🏃 Выберите уровень <b>активности</b>:",
                                   reply_markup=activity_keyboard())
    await callback.answer()
