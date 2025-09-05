from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from zoom_impact_bot import sheets

class ListRecognitionStates(StatesGroup):
    waiting_for_month = State()
    waiting_for_category = State()

def register(dp: Dispatcher):
    @dp.callback_query(F.data == "list_recs")
    async def start_list_recognitions(cb: types.CallbackQuery, state: FSMContext):
        """Start the list recognitions flow."""
        await cb.message.answer("📋 <b>List Recognitions</b>\n\n"
                              "Choose how you want to filter the recognitions:",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [InlineKeyboardButton(text="📅 Filter by Month", callback_data="filter_month")],
                                  [InlineKeyboardButton(text="🏆 Filter by Category", callback_data="filter_category")],
                                  [InlineKeyboardButton(text="📋 Show All", callback_data="show_all_recs")],
                                  [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_list_recs")]
                              ]), parse_mode="HTML")
        await cb.answer()

    @dp.callback_query(F.data == "filter_month")
    async def filter_by_month(cb: types.CallbackQuery, state: FSMContext):
        """Show month selection for filtering."""
        months = sheets.get_available_months()
        
        if not months:
            await cb.message.answer("❌ <b>No recognitions found!</b>\n\n"
                                  "There are no recognitions in the system yet.", parse_mode="HTML")
            await cb.answer()
            return
        
        # Create month selection keyboard
        keyboard = []
        for i in range(0, len(months), 2):
            row = []
            for j in range(2):
                if i + j < len(months):
                    month = months[i + j]
                    row.append(InlineKeyboardButton(
                        text=month,
                        callback_data=f"month_{month}"
                    ))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_list_recs")])
        
        await cb.message.answer("📅 <b>Select Month:</b>",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
        await cb.answer()

    @dp.callback_query(F.data == "filter_category")
    async def filter_by_category(cb: types.CallbackQuery, state: FSMContext):
        """Show category selection for filtering."""
        categories = sheets.get_categories()
        
        if not categories:
            await cb.message.answer("❌ <b>No categories found!</b>\n\n"
                                  "Please create a 'Recognition-Categories' sheet with categories in column A.", parse_mode="HTML")
            await cb.answer()
            return
        
        # Create category selection keyboard maintaining the exact order from the sheet
        keyboard = []
        for i in range(0, len(categories), 2):
            row = []
            for j in range(2):
                if i + j < len(categories):
                    category = categories[i + j]
                    row.append(InlineKeyboardButton(
                        text=category,
                        callback_data=f"cat_filter_{category}"
                    ))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_list_recs")])
        
        await cb.message.answer("🏆 <b>Select Category:</b>",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
        await cb.answer()

    @dp.callback_query(F.data == "show_all_recs")
    async def show_all_recognitions(cb: types.CallbackQuery):
        """Show all recognitions without filtering."""
        recognitions = sheets.get_recognitions()
        
        if not recognitions:
            await cb.message.answer("❌ <b>No recognitions found!</b>\n\n"
                                  "There are no recognitions in the system yet.", parse_mode="HTML")
        else:
            await display_recognitions(cb.message, recognitions, "All Recognitions")
        
        await cb.answer()

    @dp.callback_query(F.data.startswith("month_"))
    async def show_month_recognitions(cb: types.CallbackQuery):
        """Show recognitions for a specific month."""
        month = cb.data.replace("month_", "")
        recognitions = sheets.get_recognitions(month=month)
        
        if not recognitions:
            await cb.message.answer(f"❌ <b>No recognitions found for {month}!</b>", parse_mode="HTML")
        else:
            await display_recognitions(cb.message, recognitions, f"Recognitions for {month}")
        
        await cb.answer()

    @dp.callback_query(F.data.startswith("cat_filter_"))
    async def show_category_recognitions(cb: types.CallbackQuery):
        """Show recognitions for a specific category."""
        category = cb.data.replace("cat_filter_", "")
        recognitions = sheets.get_recognitions(category=category)
        
        if not recognitions:
            await cb.message.answer(f"❌ <b>No recognitions found for {category}!</b>", parse_mode="HTML")
        else:
            await display_recognitions(cb.message, recognitions, f"Recognitions for {category}")
        
        await cb.answer()

    @dp.callback_query(F.data == "cancel_list_recs")
    async def cancel_list_recognitions(cb: types.CallbackQuery, state: FSMContext):
        """Cancel the list recognitions flow."""
        await cb.message.answer("❌ <b>List Recognitions cancelled.</b>", parse_mode="HTML")
        await state.clear()
        await cb.answer()

async def display_recognitions(message: types.Message, recognitions: list, title: str):
    """Display recognitions in a formatted message."""
    if not recognitions:
        await message.answer("❌ <b>No recognitions found!</b>", parse_mode="HTML")
        return
    
    # Split into chunks if too many recognitions
    chunk_size = 10  # Telegram message limit
    chunks = [recognitions[i:i + chunk_size] for i in range(0, len(recognitions), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        text = f"📋 <b>{title}</b>\n\n"
        
        for j, rec in enumerate(chunk):
            text += f"<b>{i * chunk_size + j + 1}.</b> {rec['upline']} → {rec['downline']}\n"
            text += f"   🏆 <b>Category:</b> {rec['category']}\n"
            text += f"   📅 <b>Month:</b> {rec['month']}\n"
            if rec['remarks']:
                text += f"   💬 <b>Remarks:</b> {rec['remarks']}\n"
            text += "\n"
        
        if len(chunks) > 1:
            text += f"<i>Page {i + 1} of {len(chunks)}</i>"
        
        await message.answer(text, parse_mode="HTML")
