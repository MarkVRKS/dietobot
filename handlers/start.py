from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.main_menu import main_menu_keyboard, gender_keyboard, activity_keyboard, diet_keyboard, skip_keyboard
from services.calorie_calculator import calculate_full_profile
from services.reminder_service import refresh_user_reminders
from config import ADMIN_ID

router = Router()


class Registration(StatesGroup):
    gender = State()
    age = State()
    height = State()
    current_weight = State()
    target_weight = State()
    activity_level = State()
    diet_type = State()
    restrictions = State()
    allergies = State()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    exists = await db.user_exists(user_id)

    if exists:
        user = await db.get_user(user_id)
        if user and user.get("gender"):
            await message.answer(
                f"👋 С возвращением, {message.from_user.first_name}!",
                reply_markup=main_menu_keyboard()
            )
            return

    ref_code = None
    args = message.text.split()
    if len(args) > 1:
        ref_code = args[1]

    referred_by = None
    if ref_code:
        referrer = await db.get_user_by_referral_code(ref_code)
        if referrer:
            referred_by = referrer["user_id"]

    await db.register_user(
        user_id=user_id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        referred_by=referred_by
    )

    await state.update_data(referred_by=referred_by)
    await message.answer(
        "🏋️ <b>Добро пожаловать в бот похудения!</b>\n\n"
        "Я помогу вам контролировать питание, отслеживать вес и достигать целей.\n"
        "Для начала давайте заполним ваш профиль.\n\n"
        "👤 Укажите ваш <b>пол</b>:",
        reply_markup=gender_keyboard()
    )
    await state.set_state(Registration.gender)


@router.message(Registration.gender, F.text.in_(["Мужской", "Женский"]))
async def process_gender(message: Message, state: FSMContext):
    gender = "male" if message.text == "Мужской" else "female"
    await state.update_data(gender=gender)
    await message.answer(
        "📅 Сколько вам <b>лет</b>?",
        reply_markup=skip_keyboard()
    )
    await state.set_state(Registration.age)


@router.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    if message.text == "Пропустить":
        await state.update_data(age=30)
    else:
        try:
            age = int(message.text)
            if age < 10 or age > 100:
                await message.answer("Введите возраст от 10 до 100:")
                return
            await state.update_data(age=age)
        except ValueError:
            await message.answer("Введите числовой возраст:")
            return

    await message.answer(
        "📏 Какой у вас <b>рост</b> (в см)?",
        reply_markup=skip_keyboard()
    )
    await state.set_state(Registration.height)


@router.message(Registration.height)
async def process_height(message: Message, state: FSMContext):
    if message.text == "Пропустить":
        await state.update_data(height=170)
    else:
        try:
            height = float(message.text.replace(",", "."))
            if height < 100 or height > 250:
                await message.answer("Введите рост от 100 до 250 см:")
                return
            await state.update_data(height=height)
        except ValueError:
            await message.answer("Введите рост числом:")
            return

    await message.answer(
        "⚖️ Какой ваш <b>текущий вес</b> (в кг)?",
        reply_markup=skip_keyboard()
    )
    await state.set_state(Registration.current_weight)


@router.message(Registration.current_weight)
async def process_current_weight(message: Message, state: FSMContext):
    if message.text == "Пропустить":
        await state.update_data(current_weight=80)
    else:
        try:
            weight = float(message.text.replace(",", "."))
            if weight < 30 or weight > 300:
                await message.answer("Введите вес от 30 до 300 кг:")
                return
            await state.update_data(current_weight=weight)
        except ValueError:
            await message.answer("Введите вес числом:")
            return

    await message.answer(
        "🎯 Какой ваш <b>целевой вес</b> (в кг)?",
        reply_markup=skip_keyboard()
    )
    await state.set_state(Registration.target_weight)


@router.message(Registration.target_weight)
async def process_target_weight(message: Message, state: FSMContext):
    if message.text == "Пропустить":
        data = await state.get_data()
        await state.update_data(target_weight=data.get("current_weight", 80) - 10)
    else:
        try:
            target = float(message.text.replace(",", "."))
            if target < 30 or target > 300:
                await message.answer("Введите вес от 30 до 300 кг:")
                return
            await state.update_data(target_weight=target)
        except ValueError:
            await message.answer("Введите вес числом:")
            return

    await message.answer(
        "🏃 Уровень <b>физической активности</b>:",
        reply_markup=activity_keyboard()
    )
    await state.set_state(Registration.activity_level)


@router.message(Registration.activity_level, F.text.in_([
    "Малоподвижный", "Лёгкая активность", "Умеренная активность",
    "Высокая активность", "Очень высокая"
]))
async def process_activity(message: Message, state: FSMContext):
    level_map = {
        "Малоподвижный": "sedentary",
        "Лёгкая активность": "light",
        "Умеренная активность": "moderate",
        "Высокая активность": "active",
        "Очень высокая": "very_active",
    }
    await state.update_data(activity_level=level_map[message.text])

    await message.answer(
        "🥗 Тип <b>питания</b>:",
        reply_markup=diet_keyboard()
    )
    await state.set_state(Registration.diet_type)


@router.message(Registration.diet_type, F.text.in_([
    "Сбалансированное", "Высокобелковое", "Низкоуглеводное",
    "Кетогенное", "Вегетарианское"
]))
async def process_diet(message: Message, state: FSMContext):
    diet_map = {
        "Сбалансированное": "balanced",
        "Высокобелковое": "high_protein",
        "Низкоуглеводное": "low_carb",
        "Кетогенное": "keto",
        "Вегетарианское": "vegetarian",
    }
    await state.update_data(diet_type=diet_map[message.text])

    await message.answer(
        "🚫 Есть ли у вас <b>ограничения в питании</b>?\n"
        "(напр: без глютена, без лактозы, вегетарианство)\n"
        "Или нажмите «Пропустить»",
        reply_markup=skip_keyboard()
    )
    await state.set_state(Registration.restrictions)


@router.message(Registration.restrictions)
async def process_restrictions(message: Message, state: FSMContext):
    if message.text == "Пропустить":
        await state.update_data(restrictions="")
    else:
        await state.update_data(restrictions=message.text)

    await message.answer(
        "🤧 Есть ли у вас <b>аллергии</b>?\n"
        "(напр: на арахис, молоко, морепродукты)\n"
        "Или нажмите «Пропустить»",
        reply_markup=skip_keyboard()
    )
    await state.set_state(Registration.allergies)


@router.message(Registration.allergies)
async def process_allergies(message: Message, state: FSMContext):
    if message.text == "Пропустить":
        await state.update_data(allergies="")
    else:
        await state.update_data(allergies=message.text)

    data = await state.get_data()

    profile = calculate_full_profile(
        gender=data["gender"],
        age=data["age"],
        height=data["height"],
        current_weight=data["current_weight"],
        target_weight=data["target_weight"],
        activity_level=data["activity_level"],
        diet_type=data["diet_type"],
    )

    await db.update_user(
        message.from_user.id,
        gender=data["gender"],
        age=data["age"],
        height=data["height"],
        current_weight=data["current_weight"],
        target_weight=data["target_weight"],
        activity_level=data["activity_level"],
        diet_type=data["diet_type"],
        restrictions=data.get("restrictions", ""),
        allergies=data.get("allergies", ""),
        bmr=profile["bmr"],
        daily_calories=profile["deficit_calories"],
        daily_protein=profile["daily_protein"],
        daily_fat=profile["daily_fat"],
        daily_carbs=profile["daily_carbs"],
    )

    await db.add_weight_entry(message.from_user.id, data["current_weight"])

    await refresh_user_reminders(message.from_user.id)

    gender_text = "Мужской" if data["gender"] == "male" else "Женский"
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
        f"✅ <b>Профиль создан!</b>\n\n"
        f"👤 Пол: {gender_text}\n"
        f"📅 Возраст: {data['age']} лет\n"
        f"📏 Рост: {data['height']} см\n"
        f"⚖️ Текущий вес: {data['current_weight']} кг\n"
        f"🎯 Целевой вес: {data['target_weight']} кг\n"
        f"🏃 Активность: {activity_names.get(data['activity_level'], '')}\n"
        f"🥗 Питание: {diet_names.get(data['diet_type'], '')}\n\n"
        f"📊 <b>Расчёт калорий:</b>\n"
        f"🔥 Базовый метаболизм (BMR): {profile['bmr']} ккал\n"
        f"📊 Суточная норма: {profile['daily_calories']} ккал\n"
        f"📉 Дефицит (−20%): {profile['deficit_calories']} ккал\n\n"
        f"🥩 Белки: {profile['daily_protein']}г\n"
        f"🧈 Жиры: {profile['daily_fat']}г\n"
        f"🍞 Углеводы: {profile['daily_carbs']}г\n\n"
        f"🎯 <b>Цель:</b> сбросить {profile['weight_to_lose']} кг\n"
        f"📅 Ориентировочно: {profile['target_date']}\n\n"
        f"Формула: Миффлин-Сан Жеора\n"
        f"Дефицит: 20% от суточной нормы\n"
        f"Темп похудения: ~0.75 кг/нед\n\n"
        f"Теперь воспользуйтесь меню! 👇"
    )

    await state.clear()
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(F.text == "/admin")
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return
    from keyboards.main_menu import admin_keyboard
    await message.answer("🔧 <b>Админ-панель</b>", reply_markup=admin_keyboard())


@router.message(F.text == "◀️ Назад")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())
