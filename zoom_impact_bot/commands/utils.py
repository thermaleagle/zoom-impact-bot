from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ADMIN_IDS = {123456789}  # replace with your Telegram user_id

def roles_for(user_id:int) -> list[str]:
    return ["Admin"] if user_id in ADMIN_IDS else ["Member"]

def role_menu(roles: list[str]) -> InlineKeyboardMarkup:
    rows = []
    rows.append([InlineKeyboardButton(text="📅 Next", callback_data="next"),
                 InlineKeyboardButton(text="🗓 Week", callback_data="week")])
    rows.append([InlineKeyboardButton(text="📎 Slides", callback_data="slides"),
                 InlineKeyboardButton(text="📘 Guidelines", callback_data="guidelines")])
    rows.append([InlineKeyboardButton(text="🏆 Recognition", callback_data="recognition"),
                 InlineKeyboardButton(text="🗓 Calendar", callback_data="calendar")])
    if "Admin" in roles:
        rows.append([InlineKeyboardButton(text="➕ Save Event", callback_data="saveevent"),
                     InlineKeyboardButton(text="🎙 Assign MC", callback_data="assignmc")])
        rows.append([InlineKeyboardButton(text="✨ Assign Impact", callback_data="assignimpact"),
                     InlineKeyboardButton(text="📣 Announce", callback_data="announce")])
        rows.append([InlineKeyboardButton(text="🔁 Shift Event", callback_data="shift"),
                     InlineKeyboardButton(text="🧊 Freeze Recs", callback_data="recfreeze")])
        rows.append([InlineKeyboardButton(text="🧩 Set Template", callback_data="settemplate"),
                     InlineKeyboardButton(text="📄 Set Guidelines", callback_data="setguidelines")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
