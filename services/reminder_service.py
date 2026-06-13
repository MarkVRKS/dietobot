from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database import db

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


def setup_scheduler():
    scheduler.start()
    scheduler.add_job(check_reminders, CronTrigger(minute="*"), id="reminder_checker")


async def check_reminders():
    from datetime import datetime
    now = datetime.now()
    reminders = await db.get_all_enabled_reminders()
    for reminder in reminders:
        if reminder["hour"] == now.hour and reminder["minute"] == now.minute:
            await send_reminder(reminder)


async def send_reminder(reminder: dict):
    from aiogram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)

    user_id = reminder["user_id"]
    r_type = reminder["reminder_type"]
    first_name = reminder.get("first_name", "")

    messages = {
        "breakfast": f"🌅 {first_name}, пора завтракать! Не забудьте записать еду в дневник.",
        "lunch": f"☀️ {first_name}, время обеда! Подкрепитесь и запишите в дневник.",
        "dinner": f"🌙 {first_name}, пора ужинать! Помните о вашем плане питания.",
        "water": f"💧 {first_name}, не забудьте выпить воды!",
        "weigh_in": f"⚖️ {first_name}, самое время взвеситься и записать вес!",
        "weekly_report": f"📊 {first_name}, время еженедельного отчёта! Посмотрите статистику.",
    }

    text = messages.get(r_type, f"⏰ Напоминание: {r_type}")
    try:
        await bot.send_message(user_id, text)
    except Exception:
        pass
    finally:
        await bot.session.close()


async def refresh_user_reminders(user_id: int):
    existing_jobs = scheduler.get_jobs()
    for job in existing_jobs:
        if job.id.startswith(f"reminder_{user_id}_"):
            scheduler.remove_job(job.id)

    reminders = await db.get_reminders(user_id)
    for reminder in reminders:
        job_id = f"reminder_{user_id}_{reminder['reminder_type']}"
        try:
            scheduler.add_job(
                send_user_reminder,
                CronTrigger(hour=reminder["hour"], minute=reminder["minute"]),
                args=[user_id, reminder["reminder_type"]],
                id=job_id,
                replace_existing=True
            )
        except Exception:
            pass


async def send_user_reminder(user_id: int, reminder_type: str):
    from aiogram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)

    user = await db.get_user(user_id)
    first_name = user.get("first_name", "") if user else ""

    messages = {
        "breakfast": f"🌅 {first_name}, пора завтракать! Не забудьте записать еду в дневник.",
        "lunch": f"☀️ {first_name}, время обеда! Подкрепитесь и запишите в дневник.",
        "dinner": f"🌙 {first_name}, пора ужинать! Помните о вашем плане питания.",
        "water": f"💧 {first_name}, не забудьте выпить воды!",
        "weigh_in": f"⚖️ {first_name}, самое время взвеситься!",
        "weekly_report": f"📊 {first_name}, время еженедельного отчёта!",
    }

    text = messages.get(reminder_type, f"⏰ Напоминание")
    try:
        await bot.send_message(user_id, text)
    except Exception:
        pass
    finally:
        await bot.session.close()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
