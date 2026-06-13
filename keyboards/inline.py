from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать профиль", callback_data="edit_profile")],
        [InlineKeyboardButton(text="🔄 Пересчитать калории", callback_data="recalc_calories")],
    ])


def weight_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚖️ Записать вес", callback_data="record_weight")],
        [InlineKeyboardButton(text="📈 График прогресса", callback_data="weight_chart")],
        [InlineKeyboardButton(text="📊 История веса", callback_data="weight_history")],
    ])


def food_diary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_food")],
        [InlineKeyboardButton(text="📋 Дневник за сегодня", callback_data="today_diary")],
        [InlineKeyboardButton(text="📊 Итого за день", callback_data="day_summary")],
        [InlineKeyboardButton(text="🗑 Удалить запись", callback_data="delete_food")],
    ])


def water_inline_keyboard(current_ml: int, goal_ml: int) -> InlineKeyboardMarkup:
    progress = min(current_ml / goal_ml * 100, 100)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💧 +250 мл", callback_data="water_250")],
        [InlineKeyboardButton(text=f"💧 +500 мл", callback_data="water_500")],
        [InlineKeyboardButton(text=f"💧 +750 мл", callback_data="water_750")],
        [InlineKeyboardButton(text=f"💧 +1 литр", callback_data="water_1000")],
        [InlineKeyboardButton(text=f"📊 Прогресс: {current_ml}/{goal_ml} мл ({progress:.0f}%)", callback_data="water_progress")],
    ])


def menu_generation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сгенерировать новое меню", callback_data="generate_menu")],
        [InlineKeyboardButton(text="🛒 Список покупок", callback_data="shopping_list")],
    ])


def day_view_keyboard(day_index: int) -> InlineKeyboardMarkup:
    buttons = []
    if day_index > 0:
        buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"day_{day_index - 1}"))
    buttons.append(InlineKeyboardButton(text=f"День {day_index + 1}/7", callback_data="noop"))
    if day_index < 6:
        buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"day_{day_index + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def exercise_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏃 Кардио", callback_data="exercises_cardio")],
        [InlineKeyboardButton(text="💪 Силовые", callback_data="exercises_strength")],
        [InlineKeyboardButton(text="🧘 Гибкость", callback_data="exercises_flexibility")],
    ])


def reminder_keyboard(reminders: list) -> InlineKeyboardMarkup:
    types = {
        "breakfast": "🌅 Завтрак",
        "lunch": "☀️ Обед",
        "dinner": "🌙 Ужин",
        "water": "💧 Вода",
        "weigh_in": "⚖️ Взвешивание",
        "weekly_report": "📊 Еженедельный отчёт",
    }
    buttons = []
    for r in reminders:
        status = "✅" if r["is_enabled"] else "❌"
        name = types.get(r["reminder_type"], r["reminder_type"])
        buttons.append([InlineKeyboardButton(
            text=f"{status} {name} — {r['hour']:02d}:{r['minute']:02d}",
            callback_data=f"toggle_reminder_{r['reminder_type']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Мои данные", callback_data="my_profile")],
        [InlineKeyboardButton(text="🎯 Изменить цель", callback_data="change_target")],
        [InlineKeyboardButton(text="🥗 Тип питания", callback_data="change_diet")],
        [InlineKeyboardButton(text="🏃 Уровень активности", callback_data="change_activity")],
    ])


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no"),
        ]
    ])


def articles_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Похудение", callback_data="article_cat_weight_loss")],
        [InlineKeyboardButton(text="🥗 Питание", callback_data="article_cat_nutrition")],
        [InlineKeyboardButton(text="🥩 Белок", callback_data="article_cat_protein")],
        [InlineKeyboardButton(text="🧈 Жиры", callback_data="article_cat_fats")],
        [InlineKeyboardButton(text="🍞 Углеводы", callback_data="article_cat_carbs")],
        [InlineKeyboardButton(text="💧 Вода", callback_data="article_cat_water")],
        [InlineKeyboardButton(text="🏃 Кардио", callback_data="article_cat_cardio")],
        [InlineKeyboardButton(text="💪 Силовые", callback_data="article_cat_strength")],
        [InlineKeyboardButton(text="🔥 Мотивация", callback_data="article_cat_motivation")],
    ])


def article_keyboard(article_id: str, has_next: bool, has_prev: bool) -> InlineKeyboardMarkup:
    buttons = []
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"article_prev_{article_id}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"article_next_{article_id}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="📚 К списку", callback_data="articles_list")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def articles_list_keyboard(category: str, articles: list, page: int, per_page: int = 5) -> InlineKeyboardMarkup:
    buttons = []
    start = page * per_page
    end = start + per_page
    for a in articles[start:end]:
        buttons.append([InlineKeyboardButton(
            text=a["title"][:40],
            callback_data=f"read_article_{a['id']}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"articles_page_{category}_{page - 1}"))
    if end < len(articles):
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"articles_page_{category}_{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="articles_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def plan_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 График прогресса", callback_data="weight_chart")],
        [InlineKeyboardButton(text="🔥 План похудения", callback_data="weight_loss_plan")],
    ])


def search_product_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в дневник", callback_data="food_diary_back")],
    ])
