from aiogram import Dispatcher, types, F
from zoom_impact_bot import sheets

def register(dp: Dispatcher):
    @dp.callback_query(F.data == "slides")
    async def slides(cb: types.CallbackQuery):
        link = sheets.get_template("slides")
        await cb.message.answer(f"📎 Latest slides: {link or 'not set'}")
        await cb.answer()

    @dp.callback_query(F.data == "guidelines")
    async def guidelines(cb: types.CallbackQuery):
        link = sheets.get_template("guidelines")
        await cb.message.answer(f"📘 Guidelines: {link or 'not set'}")
        await cb.answer()
