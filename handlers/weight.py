from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.main_menu import main_menu_keyboard
from keyboards.inline import weight_actions_keyboard
from services.weight_service import create_weight_chart
from services.calorie_calculator import calculate_streak_bonus

router = Router()


class WeightStates(StatesGroup):
    entering_weight = State()
    entering_target = State()


@router.message(F.text == "🔥 План похудения")
async def plan_menu(message: Message):
    await db.record_button_click(message.from_user.id, "weight_loss_plan")
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("gender"):
        await message.answer("Сначала заполните профиль через /start")
        return

    current = user.get("current_weight", 0)
    target = user.get("target_weight", 0)
    diff = current - target

    if diff <= 0:
        await message.answer(
            "🎉 <b>Вы уже достигли цели!</b>\n\n"
            "Ваш текущий вес совпадает с целевым.\n"
            "Можете поставить новую цель в настройках.",
            reply_markup=main_menu_keyboard()
        )
        return

    weeks_needed = diff / 0.75
    months = weeks_needed / 4

    text = (
        f"🔥 <b>План похудения</b>\n\n"
        f"📊 Текущий вес: <b>{current}</b> кг\n"
        f"🎯 Целевой вес: <b>{target}</b> кг\n"
        f"📉 Нужно сбросить: <b>{diff:.1f}</b> кг\n\n"
        f"📅 Ориентировочно: <b>{int(weeks_needed)}</b> недель (~{months:.1f} мес.)\n"
        f"🏃 Темп: <b>0.75 кг/нед</b> (безопасно)\n\n"
    )

    if diff > 30:
        text += "⚠️ Рекомендуется консультация с врачом при большом лишнем весе.\n\n"
    if diff > 20:
        text += "💡 Совет: сочетайте диету с регулярными тренировками.\n"
        text += "🏃 Рекомендовано: кардио 3-4 раза в неделю + силовые 2 раза.\n\n"

    text += "✅ Ваш план питания уже рассчитан. Следуйте меню!"

    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(F.text == "⚖️ Мой вес")
async def my_weight(message: Message):
    await db.record_button_click(message.from_user.id, "weight")
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("gender"):
        await message.answer("Сначала заполните профиль через /start")
        return

    current = user.get("current_weight", 0)
    target = user.get("target_weight", 0)
    change_week = await db.get_weight_change(message.from_user.id, 7)
    change_month = await db.get_weight_change(message.from_user.id, 30)
    streak = await db.get_streak_days(message.from_user.id)
    badge = calculate_streak_bonus(streak)

    start_weight = current
    history = await db.get_weight_history(message.from_user.id, 365)
    if history:
        start_weight = history[0]["weight"]

    total_lost = start_weight - current
    if target and start_weight > target:
        total_goal = start_weight - target
        progress_pct = min((total_lost / total_goal) * 100, 100)
    else:
        progress_pct = 0

    text = (
        f"⚖️ <b>Мой вес</b>\n\n"
        f"📊 Текущий: <b>{current}</b> кг\n"
        f"🎯 Цель: <b>{target}</b> кг\n\n"
    )

    if change_week is not None:
        sign = "+" if change_week > 0 else ""
        text += f"📅 За неделю: {sign}{change_week:.1f} кг\n"
    if change_month is not None:
        sign = "+" if change_month > 0 else ""
        text += f"📅 За месяц: {sign}{change_month:.1f} кг\n"

    text += f"\n🏆 Общий прогресс: {total_lost:.1f} кг\n"
    text += f"📊 Достижение цели: {progress_pct:.0f}%\n"

    if streak > 0:
        text += f"\n🔥 Серия: {streak} дн."
        if badge:
            text += f" {badge}"

    text += "\n\n⚖️ Записать новый вес или посмотреть график?"

    await message.answer(text, reply_markup=weight_actions_keyboard())


@router.callback_query(F.data == "record_weight")
async def record_weight(callback: CallbackQuery):
    await callback.message.answer("⚖️ Введите ваш текущий вес (в кг):")
    await callback.answer()


@router.message(F.text.regexp(r"^\d+[\.,]?\d*$"))
async def process_weight_input(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user.get("gender"):
        return

    try:
        weight = float(message.text.replace(",", "."))
    except ValueError:
        return

    if weight < 30 or weight > 300:
        await message.answer("Введите реалистичный вес (30-300 кг):")
        return

    await db.add_weight_entry(message.from_user.id, weight)

    change_week = await db.get_weight_change(message.from_user.id, 7)
    change_month = await db.get_weight_change(message.from_user.id, 30)

    text = f"✅ Вес записан: <b>{weight} кг</b>\n\n"

    if change_week is not None:
        sign = "+" if change_week > 0 else ""
        text += f"📅 За неделю: {sign}{change_week:.1f} кг\n"
    if change_month is not None:
        sign = "+" if change_month > 0 else ""
        text += f"📅 За месяц: {sign}{change_month:.1f} кг\n"

    await message.answer(text, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "weight_chart")
async def weight_chart(callback: CallbackQuery):
    history = await db.get_weight_history(callback.from_user.id, 90)
    if not history:
        await callback.message.answer("Нет данных для графика. Запишите хотя бы 2 веса.")
        await callback.answer()
        return

    user = await db.get_user(callback.from_user.id)
    target = user.get("target_weight") if user else None

    chart = create_weight_chart(history, target)
    if chart:
        from aiogram.types import FSInputFile
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(chart.read())
            temp_path = f.name
        try:
            photo = FSInputFile(temp_path)
            await callback.message.answer_photo(photo, caption="📈 График прогресса веса")
        finally:
            os.unlink(temp_path)
    else:
        await callback.message.answer("Не удалось построить график.")

    await callback.answer()


@router.callback_query(F.data == "weight_history")
async def weight_history(callback: CallbackQuery):
    history = await db.get_weight_history(callback.from_user.id, 30)
    if not history:
        await callback.message.answer("Нет записей о весе.")
        await callback.answer()
        return

    text = "📊 <b>История веса (30 дней):</b>\n\n"
    for entry in reversed(history[-15:]):
        dt = entry.get("recorded_at", "")
        if isinstance(dt, str):
            dt = dt[:10]
        text += f"  {dt}: <b>{entry['weight']}</b> кг\n"

    if len(history) > 15:
        text += f"\n... и ещё {len(history) - 15} записей"

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "weight_loss_plan")
async def weight_loss_plan(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user or not user.get("gender"):
        await callback.message.answer("Сначала заполните профиль.")
        await callback.answer()
        return

    current = user.get("current_weight", 0)
    target = user.get("target_weight", 0)
    diff = current - target

    if diff <= 0:
        await callback.message.answer("🎉 Вы уже достигли цели!")
        await callback.answer()
        return

    weeks_needed = diff / 0.75
    months = weeks_needed / 4

    text = (
        f"🔥 <b>План похудения</b>\n\n"
        f"📊 Текущий вес: {current} кг\n"
        f"🎯 Целевой вес: {target} кг\n"
        f"📉 Нужно сбросить: {diff:.1f} кг\n\n"
        f"📅 Ориентировочно: {int(weeks_needed)} недель (~{months:.1f} мес.)\n"
        f"🏃 Темп: 0.75 кг/нед (безопасно)\n\n"
    )

    if diff > 30:
        text += "⚠️ Рекомендуется консультация с врачом при большом лишнем весе.\n\n"

    if diff > 20:
        text += "💡 Совет: сочетайте диету с регулярными тренировками.\n"
        text += "🏃 Рекомендовано: кардио 3-4 раза в неделю + силовые 2 раза.\n"

    text += "\n✅ Ваш план питания уже рассчитан. Следуйте меню!"

    await callback.message.answer(text, reply_markup=weight_actions_keyboard())
    await callback.answer()
