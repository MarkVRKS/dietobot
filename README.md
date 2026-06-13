# 🏋️ Telegram-бот для похудения

Полнофункциональный Telegram-бот для контроля питания, веса и похудения.

## Возможности

- 📋 Генератор меню на неделю (550+ рецептов)
- ⚖️ Трекер веса с графиками
- 🍽 Дневник питания (500+ продуктов)
- 🔥 План похудения с расчётом калорий
- 💧 Водный трекер
- ⏰ Напоминания
- 📊 Статистика и серия дней
- 📚 100+ полезных статей
- 👥 Реферальная система
- 🔧 Админ-панель

## Технологии

- Python 3.12+
- Aiogram 3.x
- SQLite
- APScheduler
- Matplotlib
- Pandas

## Установка

```bash
# Клонируйте проект
git clone <url>
cd weightloss_bot

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Установите переменные окружения
export BOT_TOKEN="ваш_токен"
export ADMIN_ID="ваш_id"

# Запустите бота
python bot.py
```

## Настройка

### Получение токена

1. Откройте @BotFather в Telegram
2. Создайте нового бота командой /newbot
3. Скопируйте токен

### Получение Admin ID

1. Откройте @userinfobot в Telegram
2. Скопируйте ваш ID

## Структура проекта

```
weightloss_bot/
├── bot.py              # Точка входа
├── config.py           # Конфигурация
├── requirements.txt    # Зависимости
├── handlers/           # Обработчики
│   ├── start.py       # Регистрация
│   ├── profile.py     # Профиль
│   ├── menu.py        # Меню
│   ├── weight.py      # Вес
│   ├── calories.py    # Калории
│   ├── water.py       # Вода
│   ├── reminders.py   # Напоминания
│   ├── statistics.py  # Статистика
│   ├── articles.py    # Статьи
│   ├── referral.py    # Рефералы
│   └── admin.py       # Админка
├── services/           # Сервисы
│   ├── calorie_calculator.py
│   ├── menu_generator.py
│   ├── weight_service.py
│   ├── reminder_service.py
│   └── shopping_list.py
├── database/           # База данных
│   ├── db.py
│   └── models.py
├── keyboards/          # Клавиатуры
│   ├── main_menu.py
│   └── inline.py
└── data/               # Данные
    ├── products.json
    ├── recipes_breakfast.json
    ├── recipes_lunch.json
    ├── recipes_dinner.json
    ├── recipes_snack.json
    ├── exercises.json
    └── menus.json
```

## Команды бота

- `/start` — Регистрация и начало работы
- `/admin` — Админ-панель (только для ADMIN_ID)

## Лицензия

MIT
