import aiosqlite
from config import DB_PATH
from typing import Optional
from datetime import datetime, date

_connection: aiosqlite.Connection | None = None


async def get_connection() -> aiosqlite.Connection:
    global _connection
    if _connection is None:
        _connection = await aiosqlite.connect(DB_PATH)
        _connection.row_factory = aiosqlite.Row
        await _connection.execute("PRAGMA journal_mode=WAL")
        await _connection.execute("PRAGMA foreign_keys=ON")
    return _connection


async def close_connection():
    global _connection
    if _connection:
        await _connection.close()
        _connection = None


async def init_db():
    conn = await get_connection()
    await conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            gender TEXT,
            age INTEGER,
            height REAL,
            current_weight REAL,
            target_weight REAL,
            activity_level TEXT,
            diet_type TEXT,
            restrictions TEXT,
            allergies TEXT,
            bmr REAL,
            daily_calories REAL,
            daily_protein REAL,
            daily_fat REAL,
            daily_carbs REAL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            referred_by INTEGER,
            referral_code TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS weight_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight REAL NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS food_diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            fat REAL NOT NULL,
            carbs REAL NOT NULL,
            weight_grams REAL NOT NULL,
            meal_type TEXT NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS water_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount_ml INTEGER NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reminder_type TEXT NOT NULL,
            hour INTEGER NOT NULL DEFAULT 8,
            minute INTEGER NOT NULL DEFAULT 0,
            is_enabled INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, reminder_type)
        );

        CREATE TABLE IF NOT EXISTS weekly_menus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            week_start DATE NOT NULL,
            menu_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS button_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            button_name TEXT NOT NULL,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS articles_read (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            article_id TEXT NOT NULL,
            read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """)
    await conn.commit()


async def register_user(user_id: int, username: str, first_name: str, referred_by: int = None):
    conn = await get_connection()
    import hashlib
    import time
    referral_code = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:8]
    try:
        await conn.execute(
            "INSERT INTO users (user_id, username, first_name, referred_by, referral_code, registered_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, first_name, referred_by, referral_code, datetime.now())
        )
        await conn.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def user_exists(user_id: int) -> bool:
    conn = await get_connection()
    cursor = await conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    return await cursor.fetchone() is not None


async def update_user(user_id: int, **kwargs):
    conn = await get_connection()
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    await conn.execute(f"UPDATE users SET {fields} WHERE user_id = ?", values)
    await conn.commit()


async def get_user(user_id: int) -> Optional[dict]:
    conn = await get_connection()
    cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if row:
        return dict(row)
    return None


async def get_user_by_referral_code(code: str) -> Optional[dict]:
    conn = await get_connection()
    cursor = await conn.execute("SELECT * FROM users WHERE referral_code = ?", (code,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_user_count() -> int:
    conn = await get_connection()
    cursor = await conn.execute("SELECT COUNT(*) FROM users")
    row = await cursor.fetchone()
    return row[0]


async def get_active_user_count() -> int:
    conn = await get_connection()
    cursor = await conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    row = await cursor.fetchone()
    return row[0]


async def get_new_users_count(days: int = 7) -> int:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT COUNT(*) FROM users WHERE registered_at >= datetime('now', ?)",
        (f"-{days} days",)
    )
    row = await cursor.fetchone()
    return row[0]


async def get_all_user_ids() -> list:
    conn = await get_connection()
    cursor = await conn.execute("SELECT user_id FROM users WHERE is_active = 1")
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def add_weight_entry(user_id: int, weight: float):
    conn = await get_connection()
    await conn.execute(
        "INSERT INTO weight_entries (user_id, weight, recorded_at) VALUES (?, ?, ?)",
        (user_id, weight, datetime.now())
    )
    await conn.commit()
    await update_user(user_id, current_weight=weight)


async def get_weight_history(user_id: int, days: int = 30) -> list:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT weight, recorded_at FROM weight_entries WHERE user_id = ? "
        "AND recorded_at >= datetime('now', ?) ORDER BY recorded_at ASC",
        (user_id, f"-{days} days")
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_latest_weight(user_id: int) -> Optional[float]:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT weight FROM weight_entries WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 1",
        (user_id,)
    )
    row = await cursor.fetchone()
    return row[0] if row else None


async def get_weight_change(user_id: int, days: int) -> Optional[float]:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT weight FROM weight_entries WHERE user_id = ? "
        "AND recorded_at >= datetime('now', ?) ORDER BY recorded_at ASC LIMIT 1",
        (user_id, f"-{days} days")
    )
    first = await cursor.fetchone()
    cursor = await conn.execute(
        "SELECT weight FROM weight_entries WHERE user_id = ? "
        "AND recorded_at >= datetime('now', ?) ORDER BY recorded_at DESC LIMIT 1",
        (user_id, f"-{days} days")
    )
    last = await cursor.fetchone()
    if first and last:
        return last[0] - first[0]
    return None


async def get_total_weight_entries(user_id: int) -> int:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT COUNT(*) FROM weight_entries WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    return row[0]


async def add_food_entry(user_id: int, product_name: str, calories: float,
                         protein: float, fat: float, carbs: float,
                         weight_grams: float, meal_type: str):
    conn = await get_connection()
    await conn.execute(
        "INSERT INTO food_diary (user_id, product_name, calories, protein, fat, carbs, weight_grams, meal_type, recorded_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, product_name, calories, protein, fat, carbs, weight_grams, meal_type, datetime.now())
    )
    await conn.commit()


async def get_food_diary_today(user_id: int) -> list:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT * FROM food_diary WHERE user_id = ? AND date(recorded_at) = date('now') "
        "ORDER BY recorded_at ASC",
        (user_id,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_food_diary_summary(user_id: int) -> dict:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT COALESCE(SUM(calories),0) as calories, "
        "COALESCE(SUM(protein),0) as protein, "
        "COALESCE(SUM(fat),0) as fat, "
        "COALESCE(SUM(carbs),0) as carbs "
        "FROM food_diary WHERE user_id = ? AND date(recorded_at) = date('now')",
        (user_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}


async def delete_food_entry(entry_id: int, user_id: int):
    conn = await get_connection()
    await conn.execute(
        "DELETE FROM food_diary WHERE id = ? AND user_id = ?",
        (entry_id, user_id)
    )
    await conn.commit()


async def add_water_entry(user_id: int, amount_ml: int):
    conn = await get_connection()
    await conn.execute(
        "INSERT INTO water_entries (user_id, amount_ml, recorded_at) VALUES (?, ?, ?)",
        (user_id, amount_ml, datetime.now())
    )
    await conn.commit()


async def get_water_today(user_id: int) -> int:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT COALESCE(SUM(amount_ml), 0) FROM water_entries "
        "WHERE user_id = ? AND date(recorded_at) = date('now')",
        (user_id,)
    )
    row = await cursor.fetchone()
    return row[0]


async def get_water_history(user_id: int, days: int = 7) -> list:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT date(recorded_at) as day, SUM(amount_ml) as total "
        "FROM water_entries WHERE user_id = ? "
        "AND recorded_at >= datetime('now', ?) "
        "GROUP BY date(recorded_at) ORDER BY day ASC",
        (user_id, f"-{days} days")
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def upsert_reminder(user_id: int, reminder_type: str, hour: int, minute: int, is_enabled: bool = True):
    conn = await get_connection()
    await conn.execute(
        "INSERT INTO reminders (user_id, reminder_type, hour, minute, is_enabled) "
        "VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(user_id, reminder_type) DO UPDATE SET hour=?, minute=?, is_enabled=?",
        (user_id, reminder_type, hour, minute, int(is_enabled), hour, minute, int(is_enabled))
    )
    await conn.commit()


async def get_reminders(user_id: int) -> list:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT * FROM reminders WHERE user_id = ? AND is_enabled = 1",
        (user_id,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_all_enabled_reminders() -> list:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT r.*, u.first_name FROM reminders r "
        "JOIN users u ON r.user_id = u.user_id "
        "WHERE r.is_enabled = 1"
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def toggle_reminder(user_id: int, reminder_type: str):
    conn = await get_connection()
    await conn.execute(
        "UPDATE reminders SET is_enabled = NOT is_enabled "
        "WHERE user_id = ? AND reminder_type = ?",
        (user_id, reminder_type)
    )
    await conn.commit()


async def save_weekly_menu(user_id: int, week_start: date, menu_json: str):
    conn = await get_connection()
    await conn.execute(
        "DELETE FROM weekly_menus WHERE user_id = ? AND week_start = ?",
        (user_id, week_start)
    )
    await conn.execute(
        "INSERT INTO weekly_menus (user_id, week_start, menu_json, created_at) VALUES (?, ?, ?, ?)",
        (user_id, week_start, menu_json, datetime.now())
    )
    await conn.commit()


async def get_weekly_menu(user_id: int, week_start: date) -> Optional[str]:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT menu_json FROM weekly_menus WHERE user_id = ? AND week_start = ?",
        (user_id, week_start)
    )
    row = await cursor.fetchone()
    return row[0] if row else None


async def record_button_click(user_id: int, button_name: str):
    conn = await get_connection()
    await conn.execute(
        "INSERT INTO button_clicks (user_id, button_name, clicked_at) VALUES (?, ?, ?)",
        (user_id, button_name, datetime.now())
    )
    await conn.commit()


async def get_button_click_stats() -> list:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT button_name, COUNT(*) as clicks FROM button_clicks "
        "GROUP BY button_name ORDER BY clicks DESC"
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_referral_stats() -> list:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT u.user_id, u.first_name, u.referral_code, "
        "COUNT(r.user_id) as referrals "
        "FROM users u LEFT JOIN users r ON u.user_id = r.referred_by "
        "GROUP BY u.user_id HAVING referrals > 0 "
        "ORDER BY referrals DESC LIMIT 20"
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_total_food_entries(user_id: int) -> int:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT COUNT(*) FROM food_diary WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    return row[0]


async def get_streak_days(user_id: int) -> int:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT DISTINCT date(recorded_at) as day FROM weight_entries "
        "WHERE user_id = ? ORDER BY day DESC",
        (user_id,)
    )
    rows = await cursor.fetchall()
    if not rows:
        return 0
    from datetime import timedelta
    today = date.today()
    streak = 0
    expected_date = today
    for row in rows:
        day = row[0]
        if isinstance(day, str):
            day = date.fromisoformat(day)
        if day == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        elif day == expected_date - timedelta(days=1):
            expected_date = day
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break
    return streak


async def record_article_read(user_id: int, article_id: str):
    conn = await get_connection()
    await conn.execute(
        "INSERT INTO articles_read (user_id, article_id, read_at) VALUES (?, ?, ?)",
        (user_id, article_id, datetime.now())
    )
    await conn.commit()


async def get_registration_stats(days: int = 30) -> list:
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT date(registered_at) as day, COUNT(*) as count "
        "FROM users WHERE registered_at >= datetime('now', ?) "
        "GROUP BY date(registered_at) ORDER BY day ASC",
        (f"-{days} days",)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
