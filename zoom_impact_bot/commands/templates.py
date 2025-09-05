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

    # Admin handlers - placeholder implementations
    @dp.callback_query(F.data == "saveevent")
    async def save_event(cb: types.CallbackQuery):
        await cb.message.answer("➕ Save Event feature coming soon.")
        await cb.answer()

    @dp.callback_query(F.data == "assignmc")
    async def assign_mc(cb: types.CallbackQuery):
        await cb.message.answer("🎙 Assign MC feature coming soon.")
        await cb.answer()

    @dp.callback_query(F.data == "assignimpact")
    async def assign_impact(cb: types.CallbackQuery):
        await cb.message.answer("✨ Assign Impact feature coming soon.")
        await cb.answer()

    @dp.callback_query(F.data == "announce")
    async def announce(cb: types.CallbackQuery):
        await cb.message.answer("📣 Announce feature coming soon.")
        await cb.answer()

    @dp.callback_query(F.data == "shift")
    async def shift_event(cb: types.CallbackQuery):
        await cb.message.answer("🔁 Shift Event feature coming soon.")
        await cb.answer()

    @dp.callback_query(F.data == "list_recs")
    async def list_recognitions(cb: types.CallbackQuery):
        await cb.message.answer("📋 List Recognitions feature coming soon.")
        await cb.answer()

    @dp.callback_query(F.data == "assignpresenter")
    async def assign_presenter(cb: types.CallbackQuery):
        await cb.message.answer("👤 <b>Assign Presenter</b> feature coming soon.", parse_mode="HTML")
        await cb.answer()

    @dp.callback_query(F.data == "separator")
    async def separator_click(cb: types.CallbackQuery):
        # Do nothing for separator clicks
        await cb.answer()
