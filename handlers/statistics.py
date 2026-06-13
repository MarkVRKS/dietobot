from aiogram import Router, F
from aiogram.types import Message
from database import db
from keyboards.main_menu import main_menu_keyboard
from services.calorie_calculator import calculate_streak_bonus

router = Router()


@router.message(F.text == "📊 Статистика")
async def statistics(message: Message):
    await db.record_button_click(message.from_user.id, "statistics")
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("gender"):
        await message.answer("Сначала заполните профиль через /start")
        return

    from datetime import datetime
    reg_date = user.get("registered_at")
    if isinstance(reg_date, str):
        reg_date = datetime.fromisoformat(reg_date.replace("Z", "+00:00"))
    if reg_date:
        days_in_system = (datetime.now() - reg_date).days
    else:
        days_in_system = 0

    total_entries = await db.get_total_weight_entries(message.from_user.id)
    food_entries = await db.get_total_food_entries(message.from_user.id)
    streak = await db.get_streak_days(message.from_user.id)
    badge = calculate_streak_bonus(streak)

    current = user.get("current_weight", 0)
    target = user.get("target_weight", 0)
    start_weight = current
    history = await db.get_weight_history(message.from_user.id, 365)
    if history:
        start_weight = history[0]["weight"]

    total_lost = start_weight - current
    if start_weight > target:
        goal_pct = min((total_lost / (start_weight - target)) * 100, 100)
    else:
        goal_pct = 100

    water_total = 0
    water_history = await db.get_water_history(message.from_user.id, 7)
    for entry in water_history:
        water_total += entry["total"]
    avg_water = water_total / 7 if water_history else 0

    from services.calorie_calculator import get_water_goal
    water_goal = get_water_goal(current)
    water_compliance = min((avg_water / water_goal) * 100, 100) if water_goal > 0 else 0

    text = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"📅 Дней в системе: <b>{days_in_system}</b>\n"
        f"⚖️ Записей веса: <b>{total_entries}</b>\n"
        f"🍽 Записей питания: <b>{food_entries}</b>\n\n"
        f"🔥 Серия дней: <b>{streak}</b> {badge}\n\n"
        f"📉 Общий прогресс: <b>{total_lost:.1f} кг</b>\n"
        f"🎯 Достижение цели: <b>{goal_pct:.0f}%</b>\n\n"
        f"💧 Среднее потребление воды: <b>{avg_water:.0f} мл/день</b>\n"
        f"💧 Соблюдение нормы: <b>{water_compliance:.0f}%</b>\n"
    )

    if total_lost > 0:
        text += f"\n🏆 Вы уже потеряли {total_lost:.1f} кг! Продолжайте!"
    elif total_lost < 0:
        text += f"\n⚠️ Вы набрали {abs(total_lost):.1f} кг. Проверьте питание."

    await message.answer(text, reply_markup=main_menu_keyboard())
