import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from zoom_impact_bot.commands import events, recognition, templates, utils, list_recognitions, event_management

def main():
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise SystemExit("BOT_TOKEN is not set. Put it in .env or export it before running.")

    bot = Bot(bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    @dp.message(Command("start"))
    async def start(m: types.Message):
        roles = utils.roles_for(m.from_user.id)
        kb = utils.role_menu(roles)
        
        print(f"User {m.from_user.id} has roles: {roles}")
        
        if "Admin" in roles:
            welcome_text = (f"👋 Welcome to Zoom Impact Bot!\n\n"
                           f"👤 <b>Your Roles:</b> {', '.join(roles)}")
        else:
            welcome_text = (f"👋 Welcome to Zoom Impact Bot!\n\n"
                           f"🔑 <b>Your User ID:</b> {m.from_user.id}\n"
                           f"👤 <b>Your Roles:</b> {', '.join(roles)}\n"
                           f"📝 <b>To get roles:</b> Add this ID to the 'UserRoles' sheet in the appropriate column")
        
        await m.answer(welcome_text, reply_markup=kb, parse_mode="HTML")

    @dp.message(Command("menu"))
    async def menu(m: types.Message):
        roles = utils.roles_for(m.from_user.id)
        kb = utils.role_menu(roles)
        
        print(f"User {m.from_user.id} has roles: {roles}")
        
        if "Admin" in roles:
            menu_text = (f"📋 Choose an action:\n\n"
                        f"👤 <b>Your Roles:</b> {', '.join(roles)}")
        else:
            menu_text = (f"📋 Choose an action:\n\n"
                        f"🔑 <b>Your User ID:</b> {m.from_user.id}\n"
                        f"👤 <b>Your Roles:</b> {', '.join(roles)}\n"
                        f"📝 <b>To get roles:</b> Add this ID to the 'UserRoles' sheet in the appropriate column")
        
        await m.answer(menu_text, reply_markup=kb, parse_mode="HTML")

    # Register command modules
    events.register(dp)
    recognition.register(dp)
    templates.register(dp)
    list_recognitions.register(dp)
    event_management.register(dp)

    logging.basicConfig(level=logging.INFO)
    logging.info("Zoom Impact Bot starting… SHEET_NAME=%s", os.getenv("SHEET_NAME", "Zoom Impact Bot Data"))

    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
