from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from zoom_impact_bot import sheets

# State machine for recognition entry
class RecognitionStates(StatesGroup):
    waiting_for_upline = State()
    waiting_for_downline = State()
    waiting_for_category = State()
    waiting_for_month = State()
    waiting_for_remarks = State()

def register(dp: Dispatcher):
    @dp.callback_query(F.data == "recognition")
    async def recog(cb: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await cb.message.answer("🏆 Let's add a recognition!\n\n"
                               "📝 <b>Step 1/5</b>: Who is the upline?\n"
                               "Please type the upline name:", parse_mode="HTML")
        await state.set_state(RecognitionStates.waiting_for_upline)
        await cb.answer()

    @dp.message(RecognitionStates.waiting_for_upline)
    async def process_upline(m: types.Message, state: FSMContext):
        await state.update_data(upline=m.text.strip())
        await m.answer("📝 <b>Step 2/5</b>: Who is the downline?\n"
                      "Please type the downline name:", parse_mode="HTML")
        await state.set_state(RecognitionStates.waiting_for_downline)

    @dp.message(RecognitionStates.waiting_for_downline)
    async def process_downline(m: types.Message, state: FSMContext):
        await state.update_data(downline=m.text.strip())
        
        # Get categories from spreadsheet
        categories = sheets.get_categories()
        
        # Check if categories were found
        if not categories:
            await m.answer("❌ <b>No categories found!</b>\n\n"
                          "Please create a 'Recognition-Categories' sheet with categories in column A.", parse_mode="HTML")
            await state.clear()
            return
        
        # Create category selection keyboard maintaining the exact order from the sheet
        keyboard = []
        
        # Display categories in the exact order they appear in the Google Sheet
        # Use 2 categories per row for better display
        for i in range(0, len(categories), 2):
            row = []
            for j in range(2):
                if i + j < len(categories):
                    category = categories[i + j]
                    row.append(InlineKeyboardButton(
                        text=category,
                        callback_data=f"cat_{category}"
                    ))
            keyboard.append(row)
        
        # Add cancel button
        keyboard.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_recognition")])
        
        await m.answer("📝 <b>Step 3/5</b>: Choose the category:",
                      reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
        await state.set_state(RecognitionStates.waiting_for_category)

    @dp.callback_query(F.data.startswith("cat_"), RecognitionStates.waiting_for_category)
    async def process_category(cb: types.CallbackQuery, state: FSMContext):
        category = cb.data.replace("cat_", "")
        await state.update_data(category=category)
        
        # Create month selection keyboard
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        keyboard = []
        for i in range(0, len(months), 3):
            row = []
            for j in range(3):
                if i + j < len(months):
                    month = months[i + j]
                    row.append(InlineKeyboardButton(
                        text=month,
                        callback_data=f"month_{month}"
                    ))
            keyboard.append(row)
        
        # Add cancel button
        keyboard.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_recognition")])
        
        await cb.message.answer("📝 <b>Step 4/5</b>: Choose the month:",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
        await state.set_state(RecognitionStates.waiting_for_month)
        await cb.answer()

    @dp.callback_query(F.data.startswith("month_"), RecognitionStates.waiting_for_month)
    async def process_month(cb: types.CallbackQuery, state: FSMContext):
        month = cb.data.replace("month_", "")
        await state.update_data(month=month)
        
        await cb.message.answer("📝 <b>Step 5/5</b>: Enter remarks/comments:\n"
                               "Please type your remarks:", parse_mode="HTML")
        await state.set_state(RecognitionStates.waiting_for_remarks)
        await cb.answer()

    @dp.message(RecognitionStates.waiting_for_remarks)
    async def process_remarks(m: types.Message, state: FSMContext):
        await state.update_data(remarks=m.text.strip())
        
        # Get all data and save
        data = await state.get_data()
        try:
            sheets.add_recognition(
                data['upline'],
                data['downline'], 
                data['category'],
                data['month'],
                data['remarks']
            )
            await m.answer(f"✅ <b>Recognition Added Successfully!</b>\n\n"
                          f"👤 <b>Upline</b>: {data['upline']}\n"
                          f"👤 <b>Downline</b>: {data['downline']}\n"
                          f"🏆 <b>Category</b>: {data['category']}\n"
                          f"📅 <b>Month</b>: {data['month']}\n"
                          f"💬 <b>Remarks</b>: {data['remarks']}", parse_mode="HTML")
        except Exception as e:
            print(f"Recognition error: {e}")
            await m.answer("❌ <b>Error adding recognition.</b>\n"
                          "Please try again or contact support.", parse_mode="HTML")
        
        await state.clear()

    @dp.callback_query(F.data == "cancel_recognition")
    async def cancel_recognition(cb: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await cb.message.answer("❌ Recognition entry cancelled.")
        await cb.answer()

    # Keep the old /rec command for backward compatibility
    @dp.message(F.text.startswith("/rec"))
    async def rec_add_legacy(m: types.Message):
        await m.answer("🏆 <b>New Recognition Flow</b>\n\n"
                      "The `/rec` command now uses a step-by-step process!\n"
                      "Click the <b>🏆 Recognition</b> button in the menu to start.", parse_mode="HTML")
