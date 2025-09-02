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
                               "📝 **Step 1/5**: Who is the upline?\n"
                               "Please type the upline name:")
        await state.set_state(RecognitionStates.waiting_for_upline)
        await cb.answer()

    @dp.message(RecognitionStates.waiting_for_upline)
    async def process_upline(m: types.Message, state: FSMContext):
        await state.update_data(upline=m.text.strip())
        await m.answer("📝 **Step 2/5**: Who is the downline?\n"
                      "Please type the downline name:")
        await state.set_state(RecognitionStates.waiting_for_downline)

    @dp.message(RecognitionStates.waiting_for_downline)
    async def process_downline(m: types.Message, state: FSMContext):
        await state.update_data(downline=m.text.strip())
        
        # Get categories from spreadsheet
        categories = sheets.get_categories()
        
        # Check if categories were found
        if not categories:
            await m.answer("❌ **No categories found!**\n\n"
                          "Please create a 'Recognition-Categories' sheet with categories in column A.")
            await state.clear()
            return
        
        # Create category selection keyboard with better organization
        keyboard = []
        
        # Group categories for better display
        percentage_cats = [cat for cat in categories if cat.endswith('%')]
        level_cats = [cat for cat in categories if cat in ['Gold', 'Platinum', 'Executive Platinum', 'Founder Platinum', 'Core']]
        lc_cats = [cat for cat in categories if 'LC' in cat or cat == 'ELC']
        pace_cats = [cat for cat in categories if 'PaceSetter' in cat]
        other_cats = [cat for cat in categories if cat not in percentage_cats + level_cats + lc_cats + pace_cats]
        
        # Add percentage categories (2 per row)
        if percentage_cats:
            for i in range(0, len(percentage_cats), 2):
                row = []
                for j in range(2):
                    if i + j < len(percentage_cats):
                        category = percentage_cats[i + j]
                        row.append(InlineKeyboardButton(
                            text=category,
                            callback_data=f"cat_{category}"
                        ))
                keyboard.append(row)
        
        # Add level categories (2 per row)
        if level_cats:
            for i in range(0, len(level_cats), 2):
                row = []
                for j in range(2):
                    if i + j < len(level_cats):
                        category = level_cats[i + j]
                        row.append(InlineKeyboardButton(
                            text=category,
                            callback_data=f"cat_{category}"
                        ))
                keyboard.append(row)
        
        # Add LC categories (2 per row)
        if lc_cats:
            for i in range(0, len(lc_cats), 2):
                row = []
                for j in range(2):
                    if i + j < len(lc_cats):
                        category = lc_cats[i + j]
                        row.append(InlineKeyboardButton(
                            text=category,
                            callback_data=f"cat_{category}"
                        ))
                keyboard.append(row)
        
        # Add PaceSetter categories (1 per row due to long names)
        if pace_cats:
            for category in pace_cats:
                keyboard.append([InlineKeyboardButton(
                    text=category,
                    callback_data=f"cat_{category}"
                )])
        
        # Add other categories (2 per row)
        if other_cats:
            for i in range(0, len(other_cats), 2):
                row = []
                for j in range(2):
                    if i + j < len(other_cats):
                        category = other_cats[i + j]
                        row.append(InlineKeyboardButton(
                            text=category,
                            callback_data=f"cat_{category}"
                        ))
                keyboard.append(row)
        
        # Add cancel button
        keyboard.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_recognition")])
        
        await m.answer("📝 **Step 3/5**: Choose the category:",
                      reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
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
        
        await cb.message.answer("📝 **Step 4/5**: Choose the month:",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
        await state.set_state(RecognitionStates.waiting_for_month)
        await cb.answer()

    @dp.callback_query(F.data.startswith("month_"), RecognitionStates.waiting_for_month)
    async def process_month(cb: types.CallbackQuery, state: FSMContext):
        month = cb.data.replace("month_", "")
        await state.update_data(month=month)
        
        await cb.message.answer("📝 **Step 5/5**: Enter remarks/comments:\n"
                               "Please type your remarks:")
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
            await m.answer(f"✅ **Recognition Added Successfully!**\n\n"
                          f"👤 **Upline**: {data['upline']}\n"
                          f"👤 **Downline**: {data['downline']}\n"
                          f"🏆 **Category**: {data['category']}\n"
                          f"📅 **Month**: {data['month']}\n"
                          f"💬 **Remarks**: {data['remarks']}")
        except Exception as e:
            print(f"Recognition error: {e}")
            await m.answer("❌ **Error adding recognition.**\n"
                          "Please try again or contact support.")
        
        await state.clear()

    @dp.callback_query(F.data == "cancel_recognition")
    async def cancel_recognition(cb: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await cb.message.answer("❌ Recognition entry cancelled.")
        await cb.answer()

    # Keep the old /rec command for backward compatibility
    @dp.message(F.text.startswith("/rec"))
    async def rec_add_legacy(m: types.Message):
        await m.answer("🏆 **New Recognition Flow**\n\n"
                      "The `/rec` command now uses a step-by-step process!\n"
                      "Click the **🏆 Recognition** button in the menu to start.")
