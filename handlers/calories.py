import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.main_menu import main_menu_keyboard
from keyboards.inline import food_diary_keyboard, search_product_keyboard
from services.calorie_calculator import calculate_product_macros
from services.weight_service import create_calories_chart
from config import DATA_DIR

router = Router()


class FoodDiaryStates(StatesGroup):
    choosing_meal = State()
    searching_product = State()
    entering_weight = State()
    choosing_product = State()


_products_cache = None


def load_products():
    global _products_cache
    if _products_cache is None:
        with open(DATA_DIR / "products.json", "r", encoding="utf-8") as f:
            _products_cache = json.load(f)
    return _products_cache


@router.message(F.text == "🍽 Дневник питания")
async def food_diary(message: Message):
    await db.record_button_click(message.from_user.id, "food_diary")
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("gender"):
        await message.answer("Сначала заполните профиль через /start")
        return

    summary = await db.get_food_diary_summary(message.from_user.id)
    daily_cal = user.get("daily_calories", 2000)
    daily_p = user.get("daily_protein", 100)
    daily_f = user.get("daily_fat", 70)
    daily_c = user.get("daily_carbs", 200)

    remaining_cal = daily_cal - summary["calories"]
    remaining_p = daily_p - summary["protein"]
    remaining_f = daily_f - summary["fat"]
    remaining_c = daily_c - summary["carbs"]

    text = (
        f"🍽 <b>Дневник питания</b>\n\n"
        f"📊 <b>Сегодня:</b>\n"
        f"🔥 Калории: {summary['calories']:.0f} / {daily_cal:.0f} (осталось {remaining_cal:.0f})\n"
        f"🥩 Белки: {summary['protein']:.0f} / {daily_p:.0f} (осталось {remaining_p:.0f})\n"
        f"🧈 Жиры: {summary['fat']:.0f} / {daily_f:.0f} (осталось {remaining_f:.0f})\n"
        f"🍞 Углеводы: {summary['carbs']:.0f} / {daily_c:.0f} (осталось {remaining_c:.0f})\n\n"
        f"Добавьте продукт или посмотрите дневник:"
    )

    await message.answer(text, reply_markup=food_diary_keyboard())


@router.callback_query(F.data == "add_food")
async def add_food_start(callback: CallbackQuery, state: FSMContext):
    from keyboards.main_menu import meal_type_keyboard
    await callback.message.answer("Выберите приём пищи:", reply_markup=meal_type_keyboard())
    await state.set_state(FoodDiaryStates.choosing_meal)
    await callback.answer()


@router.message(FoodDiaryStates.choosing_meal, F.text.in_([
    "🌅 Завтрак", "☀️ Обед", "🌙 Ужин", "🍎 Перекус"
]))
async def choose_meal(message: Message, state: FSMContext):
    meal_map = {
        "🌅 Завтрак": "breakfast",
        "☀️ Обед": "lunch",
        "🌙 Ужин": "dinner",
        "🍎 Перекус": "snack",
    }
    await state.update_data(meal_type=meal_map[message.text])
    await message.answer(
        "🔍 Введите название продукта для поиска:",
        reply_markup=search_product_keyboard()
    )
    await state.set_state(FoodDiaryStates.searching_product)


@router.message(FoodDiaryStates.searching_product)
async def search_product(message: Message, state: FSMContext):
    if message.text == "◀️ Назад в дневник":
        await state.clear()
        await message.answer("Возвращаемся в дневник.", reply_markup=food_diary_keyboard())
        return

    query = message.text.lower()
    products = load_products()
    results = [p for p in products if query in p["name"].lower()][:10]

    if not results:
        await message.answer("Продукт не найден. Попробуйте другой запрос.")
        return

    buttons = []
    for p in results:
        buttons.append([{
            "text": f"{p['name']} ({p['calories']} ккал/100г)",
            "callback_data": f"product_{products.index(p)}"
        }])

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=p["name"] + f" ({p['calories']} ккал/100г)",
                             callback_data=f"product_{products.index(p)}")]
        for p in results
    ] + [[InlineKeyboardButton(text="◀️ Назад", callback_data="food_diary_back")]])

    await state.update_data(search_results=[products.index(p) for p in results])
    await message.answer(f"Найдено {len(results)} продуктов:", reply_markup=kb)
    await state.set_state(FoodDiaryStates.choosing_product)


@router.callback_query(F.data.startswith("product_"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[1])
    products = load_products()
    if idx >= len(products):
        await callback.answer("Продукт не найден.")
        return

    product = products[idx]
    await state.update_data(product_name=product["name"],
                           calories_per_100=product["calories"],
                           protein_per_100=product["protein"],
                           fat_per_100=product["fat"],
                           carbs_per_100=product["carbs"])

    await callback.message.answer(
        f"📌 <b>{product['name']}</b>\n"
        f"На 100г: {product['calories']} ккал | Б: {product['protein']} | "
        f"Ж: {product['fat']} | У: {product['carbs']}\n\n"
        f"Введите вес порции (в граммах):"
    )
    await state.set_state(FoodDiaryStates.entering_weight)
    await callback.answer()


@router.message(FoodDiaryStates.entering_weight)
async def enter_weight(message: Message, state: FSMContext):
    if message.text == "◀️ Назад в дневник":
        await state.clear()
        await message.answer("Возвращаемся в дневник.", reply_markup=food_diary_keyboard())
        return

    try:
        weight = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите число:")
        return

    if weight <= 0 or weight > 5000:
        await message.answer("Введите реалистичный вес (1-5000 г):")
        return

    data = await state.get_data()
    macros = calculate_product_macros(
        data["calories_per_100"], data["protein_per_100"],
        data["fat_per_100"], data["carbs_per_100"], weight
    )

    await db.add_food_entry(
        message.from_user.id,
        data["product_name"],
        macros["calories"], macros["protein"],
        macros["fat"], macros["carbs"],
        weight, data["meal_type"]
    )

    text = (
        f"✅ Записано: <b>{data['product_name']}</b> ({weight}г)\n"
        f"🔥 {macros['calories']} ккал | Б: {macros['protein']}г | "
        f"Ж: {macros['fat']}г | У: {macros['carbs']}г\n\n"
        f"Добавить ещё?"
    )

    await state.clear()
    await message.answer(text, reply_markup=food_diary_keyboard())


@router.callback_query(F.data == "today_diary")
async def today_diary(callback: CallbackQuery):
    entries = await db.get_food_diary_today(callback.from_user.id)
    if not entries:
        await callback.message.answer("Дневник пуст за сегодня.")
        await callback.answer()
        return

    meal_names = {"breakfast": "🌅 Завтрак", "lunch": "☀️ Обед",
                  "dinner": "🌙 Ужин", "snack": "🍎 Перекус"}
    current_meal = None
    text = "📋 <b>Дневник за сегодня:</b>\n\n"

    for entry in entries:
        meal = meal_names.get(entry["meal_type"], entry["meal_type"])
        if meal != current_meal:
            text += f"\n<b>{meal}:</b>\n"
            current_meal = meal
        text += f"  • {entry['product_name']} ({entry['weight_grams']}г) — {entry['calories']:.0f} ккал\n"

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "day_summary")
async def day_summary(callback: CallbackQuery):
    summary = await db.get_food_diary_summary(callback.from_user.id)
    user = await db.get_user(callback.from_user.id)

    if not user:
        await callback.answer()
        return

    daily_cal = user.get("daily_calories", 2000)
    daily_p = user.get("daily_protein", 100)
    daily_f = user.get("daily_fat", 70)
    daily_c = user.get("daily_carbs", 200)

    text = (
        f"📊 <b>Итого за день:</b>\n\n"
        f"🔥 Калории: {summary['calories']:.0f} / {daily_cal:.0f} "
        f"({summary['calories']/daily_cal*100:.0f}%)\n"
        f"🥩 Белки: {summary['protein']:.0f} / {daily_p:.0f} "
        f"({summary['protein']/daily_p*100:.0f}%)\n"
        f"🧈 Жиры: {summary['fat']:.0f} / {daily_f:.0f} "
        f"({summary['fat']/daily_f*100:.0f}%)\n"
        f"🍞 Углеводы: {summary['carbs']:.0f} / {daily_c:.0f} "
        f"({summary['carbs']/daily_c*100:.0f}%)\n"
    )

    if summary["calories"] > daily_cal:
        text += f"\n⚠️ Превышение калорий на {summary['calories'] - daily_cal:.0f} ккал!"
    else:
        text += f"\n✅ Осталось {daily_cal - summary['calories']:.0f} ккал"

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "delete_food")
async def delete_food(callback: CallbackQuery):
    entries = await db.get_food_diary_today(callback.from_user.id)
    if not entries:
        await callback.message.answer("Нет записей за сегодня.")
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    for entry in entries[-10:]:
        buttons.append([InlineKeyboardButton(
            text=f"🗑 {entry['product_name']} ({entry['weight_grams']}г)",
            callback_data=f"del_food_{entry['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="food_diary_back")])

    await callback.message.answer("Выберите запись для удаления:",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("del_food_"))
async def confirm_delete_food(callback: CallbackQuery):
    entry_id = int(callback.data.split("_")[2])
    await db.delete_food_entry(entry_id, callback.from_user.id)
    await callback.message.answer("✅ Запись удалена.")
    await callback.answer()


@router.callback_query(F.data == "food_diary_back")
async def food_diary_back(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=food_diary_keyboard())
    await callback.answer()
