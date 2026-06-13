from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from config import ADMIN_ID
from keyboards.main_menu import admin_keyboard, main_menu_keyboard

router = Router()


class BroadcastState(StatesGroup):
    waiting_for_text = State()


@router.message(F.text == "📊 Статистика бота")
async def bot_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    total = await db.get_user_count()
    active = await db.get_active_user_count()
    new_week = await db.get_new_users_count(7)
    new_month = await db.get_new_users_count(30)
    button_stats = await db.get_button_click_stats()

    text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: {total}\n"
        f"✅ Активных: {active}\n"
        f"🆕 За неделю: {new_week}\n"
        f"🆕 За месяц: {new_month}\n\n"
        f"📌 <b>Статистика кнопок:</b>\n"
    )

    for stat in button_stats[:10]:
        text += f"  {stat['button_name']}: {stat['clicks']}\n"

    await message.answer(text, reply_markup=admin_keyboard())


@router.message(F.text == "👥 Пользователи")
async def user_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    total = await db.get_user_count()
    active = await db.get_active_user_count()

    text = (
        f"👥 <b>Пользователи</b>\n\n"
        f"Всего: {total}\n"
        f"Активных: {active}\n"
        f"Неактивных: {total - active}\n"
    )

    await message.answer(text, reply_markup=admin_keyboard())


@router.message(F.text == "📬 Рассылка")
async def broadcast_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📬 Введите текст рассылки:",
        reply_markup=admin_keyboard()
    )
    await state.set_state(BroadcastState.waiting_for_text)


@router.message(BroadcastState.waiting_for_text)
async def broadcast_process(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text
    user_ids = await db.get_all_user_ids()
    sent = 0
    failed = 0

    from aiogram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)

    for uid in user_ids:
        try:
            await bot.send_message(uid, f"📬 Сообщение от администратора:\n\n{text}")
            sent += 1
        except Exception:
            failed += 1

    await bot.session.close()
    await state.clear()
    await message.answer(
        f"✅ Рассылка завершена!\n"
        f"Отправлено: {sent}\n"
        f"Ошибок: {failed}",
        reply_markup=admin_keyboard()
    )


@router.message(F.text == "📈 Регистрации")
async def registration_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stats = await db.get_registration_stats(30)
    text = "📈 <b>Регистрации за 30 дней:</b>\n\n"

    for stat in stats:
        text += f"  {stat['day']}: {stat['count']} новых\n"

    if not stats:
        text += "Нет данных"

    await message.answer(text, reply_markup=admin_keyboard())


@router.message(F.text == "🏆 Топ рефералов")
async def referral_top(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stats = await db.get_referral_stats()
    text = "🏆 <b>Топ рефералов:</b>\n\n"

    for i, stat in enumerate(stats[:10], 1):
        text += f"{i}. {stat['first_name']} — {stat['referrals']} приглашений\n"

    if not stats:
        text += "Нет данных"

    await message.answer(text, reply_markup=admin_keyboard())


@router.message(F.text == "📦 Экспорт БД")
async def export_db(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    from config import DB_PATH
    import shutil
    import os

    export_path = str(DB_PATH).replace(".db", "_export.db")
    shutil.copy2(str(DB_PATH), export_path)

    from aiogram.types import FSInputFile
    try:
        await message.answer_document(
            FSInputFile(export_path),
            caption="📦 Экспорт базы данных"
        )
    except Exception:
        await message.answer("Ошибка при экспорте.")

    finally:
        if os.path.exists(export_path):
            os.unlink(export_path)

    await message.answer("Готово!", reply_markup=admin_keyboard())
