from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Меню на неделю"), KeyboardButton(text="⚖️ Мой вес")],
            [KeyboardButton(text="🍽 Дневник питания"), KeyboardButton(text="🔥 План похудения")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="💧 Вода")],
            [KeyboardButton(text="⏰ Напоминания"), KeyboardButton(text="📚 Полезные материалы")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="👥 Реферальная система")],
        ],
        resize_keyboard=True
    )


def gender_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")],
        ],
        resize_keyboard=True
    )


def activity_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Малоподвижный")],
            [KeyboardButton(text="Лёгкая активность")],
            [KeyboardButton(text="Умеренная активность")],
            [KeyboardButton(text="Высокая активность")],
            [KeyboardButton(text="Очень высокая")],
        ],
        resize_keyboard=True
    )


def diet_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сбалансированное"), KeyboardButton(text="Высокобелковое")],
            [KeyboardButton(text="Низкоуглеводное"), KeyboardButton(text="Кетогенное")],
            [KeyboardButton(text="Вегетарианское")],
        ],
        resize_keyboard=True
    )


def skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить")],
        ],
        resize_keyboard=True
    )


def back_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="◀️ Назад")],
        ],
        resize_keyboard=True
    )


def meal_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌅 Завтрак"), KeyboardButton(text="☀️ Обед")],
            [KeyboardButton(text="🌙 Ужин"), KeyboardButton(text="🍎 Перекус")],
            [KeyboardButton(text="◀️ Назад")],
        ],
        resize_keyboard=True
    )


def water_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💧 250 мл"), KeyboardButton(text="💧 500 мл")],
            [KeyboardButton(text="💧 750 мл"), KeyboardButton(text="💧 1 литр")],
            [KeyboardButton(text="◀️ Назад")],
        ],
        resize_keyboard=True
    )


def admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика бота"), KeyboardButton(text="👥 Пользователи")],
            [KeyboardButton(text="📬 Рассылка"), KeyboardButton(text="📈 Регистрации")],
            [KeyboardButton(text="🏆 Топ рефералов"), KeyboardButton(text="📦 Экспорт БД")],
            [KeyboardButton(text="◀️ Назад")],
        ],
        resize_keyboard=True
    )


def back_to_main_keyboard() -> ReplyKeyboardMarkup:
    return main_menu_keyboard()
