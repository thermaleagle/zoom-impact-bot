from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from zoom_impact_bot import sheets

def get_role_ids(role_column: int):
    """Get list of user IDs from a specific column in the UserRoles sheet."""
    try:
        ws = sheets.get_ws("UserRoles")
        # Get all values from the specified column
        role_ids = ws.col_values(role_column)
        print(f"Raw {role_column} IDs from sheet: {role_ids}")
        # Convert to integers and filter out empty values, skip header row
        role_ids = [int(role_id.strip()) for role_id in role_ids[1:] if role_id.strip().isdigit()]
        print(f"Processed {role_column} IDs: {role_ids}")
        return set(role_ids)
    except Exception as e:
        print(f"Error getting role IDs from column {role_column} in UserRoles sheet: {e}")
        return set()

def roles_for(user_id: int) -> list[str]:
    """Get all roles for a user based on their ID."""
    roles = []
    
    # Check each role column
    admin_ids = get_role_ids(1)  # Column A: Admins
    mc_ids = get_role_ids(2)     # Column B: MCs
    presenter_ids = get_role_ids(3)  # Column C: Presenters
    impact_speaker_ids = get_role_ids(4)  # Column D: Impact Speakers
    
    if user_id in admin_ids:
        roles.append("Admin")
    if user_id in mc_ids:
        roles.append("MC")
    if user_id in presenter_ids:
        roles.append("Presenter")
    if user_id in impact_speaker_ids:
        roles.append("Impact Speaker")
    
    # If no specific roles, they're a member
    if not roles:
        roles.append("Member")
    
    return roles

def role_menu(roles: list[str]) -> InlineKeyboardMarkup:
    rows = []
    
    # General Actions Section
    rows.append([InlineKeyboardButton(text="📅 Next Event", callback_data="next"),
                 InlineKeyboardButton(text="📆 Today", callback_data="today")])
    rows.append([InlineKeyboardButton(text="🗓 Week View", callback_data="week"),
                 InlineKeyboardButton(text="📎 Slides", callback_data="slides")])
    rows.append([InlineKeyboardButton(text="📘 Guidelines", callback_data="guidelines"),
                 InlineKeyboardButton(text="🏆 Recognition", callback_data="recognition")])
    rows.append([InlineKeyboardButton(text="🗓 Calendar", callback_data="calendar")])
    
    # Add separator if admin
    if "Admin" in roles:
        # Visual separator row
        rows.append([InlineKeyboardButton(text="━━━━━━━━━━━━━━━━━━━━", callback_data="separator")])
        
        # Admin Actions Section (with admin icons)
        rows.append([InlineKeyboardButton(text="👑 ➕ Save Event", callback_data="saveevent"),
                     InlineKeyboardButton(text="👑 🎙 Assign MC", callback_data="assignmc")])
        rows.append([InlineKeyboardButton(text="👑 👤 Assign Presenter", callback_data="assignpresenter"),
                     InlineKeyboardButton(text="👑 ✨ Assign Impact", callback_data="assignimpact")])
        rows.append([InlineKeyboardButton(text="👑 📣 Announce", callback_data="announce"),
                     InlineKeyboardButton(text="👑 🔁 Shift Event", callback_data="shift")])
        rows.append([InlineKeyboardButton(text="👑 📋 List Recognitions", callback_data="list_recs")])
    
    return InlineKeyboardMarkup(inline_keyboard=rows)
