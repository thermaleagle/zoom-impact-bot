from aiogram import Dispatcher, types, F
from zoom_impact_bot import sheets

def register(dp: Dispatcher):
    @dp.callback_query(F.data == "next")
    async def next_event(cb: types.CallbackQuery):
        event = sheets.get_next_event()
        if not event:
            await cb.message.answer("⚠️ No upcoming events scheduled.")
        else:
            typ = event.get("type", "Event")
            date = event.get("date", "")
            time = event.get("time", "")
            zoom = event.get("zoom_link", "<no link>")
            mc = event.get("mc", "TBD")
            imp = event.get("impact", "TBD")
            text = (f"📅 Next Event\n"
                    f"Type: {typ}\n"
                    f"When: {date} {time} (IST)\n"
                    f"MC: {mc}\n"
                    f"Impact: {imp}\n"
                    f"Zoom: {zoom}")
            await cb.message.answer(text)
        await cb.answer()

    @dp.callback_query(F.data == "week")
    async def week(cb: types.CallbackQuery):
        await cb.message.answer("🗓 Week view coming soon.")
        await cb.answer()
