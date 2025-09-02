from aiogram import Dispatcher, types, F
from zoom_impact_bot import sheets

def register(dp: Dispatcher):
    @dp.callback_query(F.data == "recognition")
    async def recog(cb: types.CallbackQuery):
        await cb.message.answer("🏆 Add recognition via:\n"
                                "`/rec Upline | Downline | Category | Month | Remarks`",
                                parse_mode="Markdown")
        await cb.answer()

    @dp.message(F.text.startswith("/rec"))
    async def rec_add(m: types.Message):
        try:
            _, data = m.text.split(" ", 1)
            parts = [x.strip() for x in data.split("|")]
            if len(parts) < 5:
                raise ValueError("incomplete")
            upline, downline, category, month, remarks = parts[:5]
            sheets.add_recognition(upline, downline, category, month, remarks)
            await m.answer(f"✅ Recognition added for {downline} in {category}.")
        except Exception:
            await m.answer("⚠️ Error. Format:\n"
                           "`/rec Upline | Downline | Category | Month | Remarks`",
                           parse_mode="Markdown")
