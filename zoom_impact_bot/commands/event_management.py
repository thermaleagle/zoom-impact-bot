from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from zoom_impact_bot import sheets
from datetime import datetime, date
from zoneinfo import ZoneInfo
import re

TZ = ZoneInfo("Asia/Kolkata")

# FSM States for Save Event wizard
class SaveEventStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_zoom = State()
    waiting_for_mc = State()
    waiting_for_presenter = State()
    waiting_for_impacts = State()

# FSM States for Assignment flows
class AssignmentStates(StatesGroup):
    waiting_for_event_selection = State()
    waiting_for_mc_assignment = State()
    waiting_for_presenter_assignment = State()
    waiting_for_impact_assignment = State()

# In-memory storage for wizard state
wizard_data = {}
assignment_data = {}

def register(dp: Dispatcher):
    # Save Event wizard handlers
    @dp.callback_query(F.data == "saveevent")
    async def start_save_event(cb: types.CallbackQuery, state: FSMContext):
        """Start the Save Event wizard."""
        try:
            event_types = sheets.get_event_types()
            if not event_types:
                await cb.message.answer("❌ <b>No event types found!</b>\n\nPlease add event types to the 'EventTypes' sheet in column A first.", parse_mode="HTML")
                await cb.answer()
                return
            
            # Create inline keyboard for event types
            buttons = []
            for event_type in event_types:
                buttons.append([InlineKeyboardButton(text=event_type, callback_data=f"event_type_{event_type}")])
            
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_save_event")])
            
            await cb.message.answer("📝 <b>Save Event</b>\n\n<b>Step 1/7:</b> Select event type:", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(SaveEventStates.waiting_for_type)
            await cb.answer()
            
        except ValueError as e:
            await cb.message.answer(f"❌ <b>Error:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error starting Save Event:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data.startswith("event_type_"))
    async def select_event_type(cb: types.CallbackQuery, state: FSMContext):
        """Handle event type selection."""
        event_type = cb.data.replace("event_type_", "")
        wizard_data[cb.from_user.id] = {"type": event_type}
        
        await cb.message.answer("📅 <b>Step 2/7:</b> Enter event date (YYYY-MM-DD):\n\nExample: 2024-01-15", parse_mode="HTML")
        await state.set_state(SaveEventStates.waiting_for_date)
        await cb.answer()

    @dp.message(SaveEventStates.waiting_for_date)
    async def process_date(m: types.Message, state: FSMContext):
        """Process date input."""
        try:
            # Validate date format
            date_obj = datetime.strptime(m.text.strip(), "%Y-%m-%d").date()
            wizard_data[m.from_user.id]["date"] = m.text.strip()
            
            await m.answer("🕐 <b>Step 3/7:</b> Enter event time (HH:MM):\n\nExample: 20:30", parse_mode="HTML")
            await state.set_state(SaveEventStates.waiting_for_time)
            
        except ValueError:
            await m.answer("❌ <b>Invalid date format!</b>\n\nPlease use YYYY-MM-DD format.\nExample: 2024-01-15", parse_mode="HTML")

    @dp.message(SaveEventStates.waiting_for_time)
    async def process_time(m: types.Message, state: FSMContext):
        """Process time input."""
        try:
            # Validate time format
            time_obj = datetime.strptime(m.text.strip(), "%H:%M").time()
            wizard_data[m.from_user.id]["time"] = m.text.strip()
            
            await m.answer("🔗 <b>Step 4/7:</b> Enter Zoom link (must start with http):\n\nExample: https://zoom.us/j/123456789", parse_mode="HTML")
            await state.set_state(SaveEventStates.waiting_for_zoom)
            
        except ValueError:
            await m.answer("❌ <b>Invalid time format!</b>\n\nPlease use HH:MM format.\nExample: 20:30", parse_mode="HTML")

    @dp.message(SaveEventStates.waiting_for_zoom)
    async def process_zoom_link(m: types.Message, state: FSMContext):
        """Process Zoom link input."""
        zoom_link = m.text.strip()
        if not zoom_link.startswith("http"):
            await m.answer("❌ <b>Invalid Zoom link!</b>\n\nLink must start with 'http'.\nExample: https://zoom.us/j/123456789", parse_mode="HTML")
            return
        
        wizard_data[m.from_user.id]["zoom_link"] = zoom_link
        
        # Get MCs for selection
        try:
            mcs, _, _ = sheets.get_user_roles()
            if not mcs:
                await m.answer("❌ <b>No MCs found!</b>\n\nPlease add MCs to the 'UserRoles' sheet in column B first.", parse_mode="HTML")
                return
            
            buttons = []
            for mc in mcs:
                buttons.append([InlineKeyboardButton(text=mc, callback_data=f"mc_{mc}")])
            
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_save_event")])
            
            await m.answer("🎙 <b>Step 5/7:</b> Select MC:", 
                          reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                          parse_mode="HTML")
            await state.set_state(SaveEventStates.waiting_for_mc)
            
        except Exception as e:
            await m.answer(f"❌ <b>Error getting MCs:</b> {str(e)}", parse_mode="HTML")

    @dp.callback_query(F.data.startswith("mc_"))
    async def select_mc(cb: types.CallbackQuery, state: FSMContext):
        """Handle MC selection."""
        mc = cb.data.replace("mc_", "")
        wizard_data[cb.from_user.id]["mc"] = mc
        
        # Get Presenters for selection
        try:
            _, presenters, _ = sheets.get_user_roles()
            if not presenters:
                await cb.message.answer("❌ <b>No Presenters found!</b>\n\nPlease add Presenters to the 'UserRoles' sheet in column C first.", parse_mode="HTML")
                await cb.answer()
                return
            
            buttons = []
            for presenter in presenters:
                buttons.append([InlineKeyboardButton(text=presenter, callback_data=f"presenter_{presenter}")])
            
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_save_event")])
            
            await cb.message.answer("🧑‍🏫 <b>Step 6/7:</b> Select Presenter:", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(SaveEventStates.waiting_for_presenter)
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error getting Presenters:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data.startswith("presenter_"))
    async def select_presenter(cb: types.CallbackQuery, state: FSMContext):
        """Handle Presenter selection."""
        presenter = cb.data.replace("presenter_", "")
        wizard_data[cb.from_user.id]["presenter"] = presenter
        
        # Get Impact Speakers for multi-select
        try:
            _, _, impacts = sheets.get_user_roles()
            if not impacts:
                await cb.message.answer("❌ <b>No Impact Speakers found!</b>\n\nPlease add Impact Speakers to the 'UserRoles' sheet in column D first.", parse_mode="HTML")
                await cb.answer()
                return
            
            # Initialize selected impacts
            wizard_data[cb.from_user.id]["selected_impacts"] = []
            
            buttons = []
            for impact in impacts:
                buttons.append([InlineKeyboardButton(text=f"☐ {impact}", callback_data=f"toggle_impact_{impact}")])
            
            buttons.append([InlineKeyboardButton(text="💾 Save Event", callback_data="save_event_final")])
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_save_event")])
            
            await cb.message.answer("✨ <b>Step 7/7:</b> Select Impact Speaker(s) (multi-select):\n\nClick to toggle selection, then click 'Save Event'", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(SaveEventStates.waiting_for_impacts)
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error getting Impact Speakers:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data.startswith("toggle_impact_"))
    async def toggle_impact(cb: types.CallbackQuery, state: FSMContext):
        """Toggle impact speaker selection."""
        impact = cb.data.replace("toggle_impact_", "")
        user_id = cb.from_user.id
        
        if user_id not in wizard_data:
            await cb.answer("❌ Session expired. Please start over.")
            return
        
        if "selected_impacts" not in wizard_data[user_id]:
            wizard_data[user_id]["selected_impacts"] = []
        
        selected_impacts = wizard_data[user_id]["selected_impacts"]
        
        if impact in selected_impacts:
            selected_impacts.remove(impact)
        else:
            selected_impacts.append(impact)
        
        # Update the keyboard
        try:
            _, _, impacts = sheets.get_user_roles()
            buttons = []
            for imp in impacts:
                prefix = "☑" if imp in selected_impacts else "☐"
                buttons.append([InlineKeyboardButton(text=f"{prefix} {imp}", callback_data=f"toggle_impact_{imp}")])
            
            buttons.append([InlineKeyboardButton(text="💾 Save Event", callback_data="save_event_final")])
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_save_event")])
            
            await cb.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
            await cb.answer()
            
        except Exception as e:
            await cb.answer(f"❌ Error updating selection: {str(e)}")

    @dp.callback_query(F.data == "save_event_final")
    async def save_event_final(cb: types.CallbackQuery, state: FSMContext):
        """Save the event to the sheet."""
        user_id = cb.from_user.id
        
        if user_id not in wizard_data:
            await cb.answer("❌ Session expired. Please start over.")
            return
        
        data = wizard_data[user_id]
        
        try:
            # Append row to Events sheet
            ws = sheets.get_ws("Events")
            impact_str = ", ".join(data.get("selected_impacts", []))
            
            row_data = [
                data["type"],
                data["date"],
                data["time"],
                data["zoom_link"],
                data["mc"],
                data["presenter"],
                impact_str,
                "Scheduled",  # status
                ""  # notes
            ]
            
            ws.append_row(row_data)
            
            # Clean up
            del wizard_data[user_id]
            await state.clear()
            
            await cb.message.answer("✅ <b>Event saved successfully!</b>\n\n"
                                  f"<b>Type:</b> {data['type']}\n"
                                  f"<b>Date:</b> {data['date']}\n"
                                  f"<b>Time:</b> {data['time']}\n"
                                  f"<b>MC:</b> {data['mc']}\n"
                                  f"<b>Presenter:</b> {data['presenter']}\n"
                                  f"<b>Impact:</b> {impact_str}", parse_mode="HTML")
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error saving event:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data == "cancel_save_event")
    async def cancel_save_event(cb: types.CallbackQuery, state: FSMContext):
        """Cancel the Save Event wizard."""
        user_id = cb.from_user.id
        if user_id in wizard_data:
            del wizard_data[user_id]
        
        await state.clear()
        await cb.message.answer("❌ Save Event cancelled.", parse_mode="HTML")
        await cb.answer()

    # Assignment handlers
    @dp.callback_query(F.data == "assignmc")
    async def start_assign_mc(cb: types.CallbackQuery, state: FSMContext):
        """Start MC assignment flow."""
        try:
            events = sheets.list_upcoming_events(14)  # Next 14 days
            if not events:
                await cb.message.answer("⚠️ <b>No upcoming events found!</b>\n\nNo events scheduled in the next 14 days.", parse_mode="HTML")
                await cb.answer()
                return
            
            buttons = []
            for row_idx, event in events:
                event_text = f"{event['date']} {event['time']} — {event['type']}"
                buttons.append([InlineKeyboardButton(text=event_text, callback_data=f"assign_mc_event_{row_idx}")])
            
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_assignment")])
            
            await cb.message.answer("🎙 <b>Assign MC</b>\n\nSelect an event to assign MC:", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(AssignmentStates.waiting_for_event_selection)
            assignment_data[cb.from_user.id] = {"type": "mc"}
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data.startswith("assign_mc_event_"))
    async def select_event_for_mc_assignment(cb: types.CallbackQuery, state: FSMContext):
        """Handle event selection for MC assignment."""
        row_idx = int(cb.data.replace("assign_mc_event_", ""))
        assignment_data[cb.from_user.id]["event_row"] = row_idx
        
        try:
            mcs, _, _ = sheets.get_user_roles()
            if not mcs:
                await cb.message.answer("❌ <b>No MCs found!</b>\n\nPlease add MCs to the 'UserRoles' sheet in column B first.", parse_mode="HTML")
                await cb.answer()
                return
            
            buttons = []
            for mc in mcs:
                buttons.append([InlineKeyboardButton(text=mc, callback_data=f"assign_mc_{mc}")])
            
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_assignment")])
            
            await cb.message.answer("🎙 <b>Select MC:</b>", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(AssignmentStates.waiting_for_mc_assignment)
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error getting MCs:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data.startswith("assign_mc_"))
    async def assign_mc_final(cb: types.CallbackQuery, state: FSMContext):
        """Finalize MC assignment."""
        mc = cb.data.replace("assign_mc_", "")
        user_id = cb.from_user.id
        
        if user_id not in assignment_data:
            await cb.answer("❌ Session expired. Please start over.")
            return
        
        try:
            row_idx = assignment_data[user_id]["event_row"]
            sheets.update_event_roles(row_idx, mc=mc)
            
            # Clean up
            del assignment_data[user_id]
            await state.clear()
            
            await cb.message.answer(f"✅ <b>MC assigned successfully!</b>\n\n<b>MC:</b> {mc}", parse_mode="HTML")
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error assigning MC:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    # Similar handlers for Presenter and Impact assignments would follow the same pattern
    # For brevity, I'll implement the key ones and mention the pattern

    @dp.callback_query(F.data == "assignpresenter")
    async def start_assign_presenter(cb: types.CallbackQuery, state: FSMContext):
        """Start Presenter assignment flow."""
        try:
            events = sheets.list_upcoming_events(14)
            if not events:
                await cb.message.answer("⚠️ <b>No upcoming events found!</b>\n\nNo events scheduled in the next 14 days.", parse_mode="HTML")
                await cb.answer()
                return
            
            buttons = []
            for row_idx, event in events:
                event_text = f"{event['date']} {event['time']} — {event['type']}"
                buttons.append([InlineKeyboardButton(text=event_text, callback_data=f"assign_presenter_event_{row_idx}")])
            
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_assignment")])
            
            await cb.message.answer("🧑‍🏫 <b>Assign Presenter</b>\n\nSelect an event to assign Presenter:", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(AssignmentStates.waiting_for_event_selection)
            assignment_data[cb.from_user.id] = {"type": "presenter"}
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data == "assignimpact")
    async def start_assign_impact(cb: types.CallbackQuery, state: FSMContext):
        """Start Impact assignment flow."""
        try:
            events = sheets.list_upcoming_events(14)
            if not events:
                await cb.message.answer("⚠️ <b>No upcoming events found!</b>\n\nNo events scheduled in the next 14 days.", parse_mode="HTML")
                await cb.answer()
                return
            
            buttons = []
            for row_idx, event in events:
                event_text = f"{event['date']} {event['time']} — {event['type']}"
                buttons.append([InlineKeyboardButton(text=event_text, callback_data=f"assign_impact_event_{row_idx}")])
            
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_assignment")])
            
            await cb.message.answer("✨ <b>Assign Impact Speaker(s)</b>\n\nSelect an event to assign Impact Speaker(s):", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(AssignmentStates.waiting_for_event_selection)
            assignment_data[cb.from_user.id] = {"type": "impact"}
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    # Presenter assignment handlers
    @dp.callback_query(F.data.startswith("assign_presenter_event_"))
    async def select_event_for_presenter_assignment(cb: types.CallbackQuery, state: FSMContext):
        """Handle event selection for Presenter assignment."""
        row_idx = int(cb.data.replace("assign_presenter_event_", ""))
        assignment_data[cb.from_user.id]["event_row"] = row_idx
        
        try:
            _, presenters, _ = sheets.get_user_roles()
            if not presenters:
                await cb.message.answer("❌ <b>No Presenters found!</b>\n\nPlease add Presenters to the 'UserRoles' sheet in column C first.", parse_mode="HTML")
                await cb.answer()
                return
            
            buttons = []
            for presenter in presenters:
                buttons.append([InlineKeyboardButton(text=presenter, callback_data=f"assign_presenter_{presenter}")])
            
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_assignment")])
            
            await cb.message.answer("🧑‍🏫 <b>Select Presenter:</b>", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(AssignmentStates.waiting_for_presenter_assignment)
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error getting Presenters:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data.startswith("assign_presenter_"))
    async def assign_presenter_final(cb: types.CallbackQuery, state: FSMContext):
        """Finalize Presenter assignment."""
        presenter = cb.data.replace("assign_presenter_", "")
        user_id = cb.from_user.id
        
        if user_id not in assignment_data:
            await cb.answer("❌ Session expired. Please start over.")
            return
        
        try:
            row_idx = assignment_data[user_id]["event_row"]
            sheets.update_event_roles(row_idx, presenter=presenter)
            
            # Clean up
            del assignment_data[user_id]
            await state.clear()
            
            await cb.message.answer(f"✅ <b>Presenter assigned successfully!</b>\n\n<b>Presenter:</b> {presenter}", parse_mode="HTML")
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error assigning Presenter:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    # Impact assignment handlers
    @dp.callback_query(F.data.startswith("assign_impact_event_"))
    async def select_event_for_impact_assignment(cb: types.CallbackQuery, state: FSMContext):
        """Handle event selection for Impact assignment."""
        row_idx = int(cb.data.replace("assign_impact_event_", ""))
        assignment_data[cb.from_user.id]["event_row"] = row_idx
        assignment_data[cb.from_user.id]["selected_impacts"] = []
        
        try:
            _, _, impacts = sheets.get_user_roles()
            if not impacts:
                await cb.message.answer("❌ <b>No Impact Speakers found!</b>\n\nPlease add Impact Speakers to the 'UserRoles' sheet in column D first.", parse_mode="HTML")
                await cb.answer()
                return
            
            buttons = []
            for impact in impacts:
                buttons.append([InlineKeyboardButton(text=f"☐ {impact}", callback_data=f"toggle_assign_impact_{impact}")])
            
            buttons.append([InlineKeyboardButton(text="💾 Save Assignment", callback_data="save_impact_assignment")])
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_assignment")])
            
            await cb.message.answer("✨ <b>Select Impact Speaker(s) (multi-select):</b>\n\nClick to toggle selection, then click 'Save Assignment'", 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
                                  parse_mode="HTML")
            await state.set_state(AssignmentStates.waiting_for_impact_assignment)
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error getting Impact Speakers:</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data.startswith("toggle_assign_impact_"))
    async def toggle_assign_impact(cb: types.CallbackQuery, state: FSMContext):
        """Toggle impact speaker selection for assignment."""
        impact = cb.data.replace("toggle_assign_impact_", "")
        user_id = cb.from_user.id
        
        if user_id not in assignment_data:
            await cb.answer("❌ Session expired. Please start over.")
            return
        
        if "selected_impacts" not in assignment_data[user_id]:
            assignment_data[user_id]["selected_impacts"] = []
        
        selected_impacts = assignment_data[user_id]["selected_impacts"]
        
        if impact in selected_impacts:
            selected_impacts.remove(impact)
        else:
            selected_impacts.append(impact)
        
        # Update the keyboard
        try:
            _, _, impacts = sheets.get_user_roles()
            buttons = []
            for imp in impacts:
                prefix = "☑" if imp in selected_impacts else "☐"
                buttons.append([InlineKeyboardButton(text=f"{prefix} {imp}", callback_data=f"toggle_assign_impact_{imp}")])
            
            buttons.append([InlineKeyboardButton(text="💾 Save Assignment", callback_data="save_impact_assignment")])
            buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_assignment")])
            
            await cb.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
            await cb.answer()
            
        except Exception as e:
            await cb.answer(f"❌ Error updating selection: {str(e)}")

    @dp.callback_query(F.data == "save_impact_assignment")
    async def save_impact_assignment_final(cb: types.CallbackQuery, state: FSMContext):
        """Finalize Impact assignment."""
        user_id = cb.from_user.id
        
        if user_id not in assignment_data:
            await cb.answer("❌ Session expired. Please start over.")
            return
        
        try:
            row_idx = assignment_data[user_id]["event_row"]
            selected_impacts = assignment_data[user_id].get("selected_impacts", [])
            
            sheets.update_event_roles(row_idx, impacts=selected_impacts)
            
            # Clean up
            del assignment_data[user_id]
            await state.clear()
            
            impact_str = ", ".join(selected_impacts) if selected_impacts else "None"
            await cb.message.answer(f"✅ <b>Impact Speaker(s) assigned successfully!</b>\n\n<b>Impact:</b> {impact_str}", parse_mode="HTML")
            await cb.answer()
            
        except Exception as e:
            await cb.message.answer(f"❌ <b>Error assigning Impact Speaker(s):</b> {str(e)}", parse_mode="HTML")
            await cb.answer()

    @dp.callback_query(F.data == "cancel_assignment")
    async def cancel_assignment(cb: types.CallbackQuery, state: FSMContext):
        """Cancel assignment flow."""
        user_id = cb.from_user.id
        if user_id in assignment_data:
            del assignment_data[user_id]
        
        await state.clear()
        await cb.message.answer("❌ Assignment cancelled.", parse_mode="HTML")
        await cb.answer()
