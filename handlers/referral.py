from aiogram import Router, F
from aiogram.types import Message
from database import db
from keyboards.main_menu import main_menu_keyboard

router = Router()


@router.message(F.text == "👥 Реферальная система")
async def referral_system(message: Message):
    await db.record_button_click(message.from_user.id, "referral")
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала заполните профиль через /start")
        return

    referral_code = user.get("referral_code", "")
    bot_username = (await message.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={referral_code}"

    from database.db import get_connection
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT COUNT(*) FROM users WHERE referred_by = ?",
        (message.from_user.id,)
    )
    row = await cursor.fetchone()
    invited_count = row[0] if row else 0

    text = (
        f"👥 <b>Реферальная система</b>\n\n"
        f"Приглашайте друзей и получайте статистику!\n\n"
        f"🔗 Ваша ссылка:\n<code>{referral_link}</code>\n\n"
        f"📊 Приглашено: <b>{invited_count}</b> человек\n\n"
        f"Как работает:\n"
        f"1. Отправьте ссылку другу\n"
        f"2. Друг нажимает /start с вашей ссылкой\n"
        f"3. Вы увидите статистику в профиле\n\n"
        f"Без начисления денег — только статистика!"
    )

    await message.answer(text, reply_markup=main_menu_keyboard())
