from aiogram import Dispatcher, types, F
from zoom_impact_bot import sheets
from datetime import date
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Kolkata")

def register(dp: Dispatcher):
    @dp.callback_query(F.data == "next")
    async def next_event(cb: types.CallbackQuery):
        """Show the nearest upcoming event."""
        event = sheets.get_next_event()
        if not event:
            await cb.message.answer("⚠️ <b>No upcoming events scheduled.</b>", parse_mode="HTML")
        else:
            typ = event.get("type", "Event")
            event_date = event.get("date", "")
            event_time = event.get("time", "")
            zoom = event.get("zoom_link", "<no link>")
            mc = event.get("mc", "TBD")
            presenter = event.get("presenter", "TBD")
            impact = event.get("impact", "TBD")
            
            text = (f"📅 <b>Next Event</b>\n"
                    f"<b>Type:</b> {typ}\n"
                    f"<b>When:</b> {event_date} {event_time} (IST)\n"
                    f"<b>Zoom:</b> {zoom}\n\n"
                    f"🎙 <b>MC:</b> {mc}\n"
                    f"🧑‍🏫 <b>Presenter:</b> {presenter}\n"
                    f"✨ <b>Impact:</b> {impact}")
            await cb.message.answer(text, parse_mode="HTML")
        await cb.answer()

    @dp.callback_query(F.data == "today")
    async def today_events(cb: types.CallbackQuery):
        """Show all events for today."""
        try:
            today = date.today()
            events = sheets.list_events_for_date(today)
            
            if not events:
                await cb.message.answer("No events today.", parse_mode="HTML")
            else:
                text = "📆 <b>Today's Events</b>\n\n"
                
                for event in events:
                    event_time = event.get("time", "")
                    event_type = event.get("type", "Event")
                    mc = event.get("mc", "TBD")
                    presenter = event.get("presenter", "TBD")
                    impact = event.get("impact", "TBD")
                    
                    text += f"{event_time} — {event_type}\n"
                    text += f"🎙 MC: {mc} | 🧑‍🏫 Presenter: {presenter} | ✨ Impact: {impact}\n\n"
                
                await cb.message.answer(text, parse_mode="HTML")
                
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error getting today's events:</b> {str(e)}", parse_mode="HTML")
        
        await cb.answer()

    @dp.callback_query(F.data == "week")
    async def week_view(cb: types.CallbackQuery):
        """Show events for the next 7 days."""
        try:
            events = sheets.list_upcoming_events(7)
            
            if not events:
                await cb.message.answer("⚠️ <b>No events in the next 7 days.</b>", parse_mode="HTML")
            else:
                text = "🗓 <b>Week View (Next 7 Days)</b>\n\n"
                
                for row_idx, event in events:
                    event_date = event.get("date", "")
                    event_time = event.get("time", "")
                    event_type = event.get("type", "Event")
                    mc = event.get("mc", "TBD")
                    presenter = event.get("presenter", "TBD")
                    impact = event.get("impact", "TBD")
                    
                    # Format date nicely
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(event_date, "%Y-%m-%d")
                        day_name = date_obj.strftime("%a")
                        day_num = date_obj.strftime("%d")
                        month_name = date_obj.strftime("%b")
                        formatted_date = f"{day_name} {day_num} {month_name}"
                    except:
                        formatted_date = event_date
                    
                    text += f"{formatted_date}, {event_time} — {event_type}\n"
                    text += f"🎙 MC: {mc} | 🧑‍🏫 Presenter: {presenter} | ✨ Impact: {impact}\n\n"
                
                await cb.message.answer(text, parse_mode="HTML")
                
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error getting week view:</b> {str(e)}", parse_mode="HTML")
        
        await cb.answer()

    @dp.callback_query(F.data == "calendar")
    async def calendar(cb: types.CallbackQuery):
        await cb.message.answer("📅 <b>Calendar view coming soon.</b>", parse_mode="HTML")
        await cb.answer()
