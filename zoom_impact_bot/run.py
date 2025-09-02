import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv

from zoom_impact_bot.commands import events, recognition, templates, utils

def main():
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise SystemExit("BOT_TOKEN is not set. Put it in .env or export it before running.")

    bot = Bot(bot_token)
    dp = Dispatcher()

    @dp.message(Command("menu"))
    async def menu(m: types.Message):
        roles = utils.roles_for(m.from_user.id)
        kb = utils.role_menu(roles)
        await m.answer("📋 Choose an action:", reply_markup=kb)

    # Register command modules
    events.register(dp)
    recognition.register(dp)
    templates.register(dp)

    logging.basicConfig(level=logging.INFO)
    logging.info("Zoom Impact Bot starting… SHEET_NAME=%s", os.getenv("SHEET_NAME", "Zoom Impact Bot Data"))

    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
