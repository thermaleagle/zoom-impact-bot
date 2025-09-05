import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Kolkata")
SHEET_NAME = os.getenv("SHEET_NAME", "Zoom Impact Bot Data")
SERVICE_JSON = os.getenv("GOOGLE_SERVICE_JSON", "service_account.json")

# Debug information for Railway deployment
print("Environment check:")
print(f"SHEET_NAME: {SHEET_NAME}")
print(f"SERVICE_JSON type: {type(SERVICE_JSON)}")
print(f"SERVICE_JSON length: {len(SERVICE_JSON) if SERVICE_JSON else 'None'}")
print(f"SERVICE_JSON starts with '{{': {SERVICE_JSON.startswith('{') if SERVICE_JSON else False}")

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Handle both file path and JSON content for Railway deployment
try:
    if SERVICE_JSON.startswith('{'):
        # JSON content provided directly (Railway deployment)
        service_account_info = json.loads(SERVICE_JSON)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    else:
        # File path provided (local development)
        # Check if file exists before trying to use it
        if os.path.exists(SERVICE_JSON):
            creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_JSON, scope)
        else:
            # If file doesn't exist, try to parse as JSON content
            try:
                service_account_info = json.loads(SERVICE_JSON)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
            except json.JSONDecodeError:
                raise FileNotFoundError(f"Service account file '{SERVICE_JSON}' not found and GOOGLE_SERVICE_JSON is not valid JSON")
except Exception as e:
    print(f"Error initializing Google Sheets credentials: {e}")
    print(f"SERVICE_JSON value: {SERVICE_JSON[:100]}..." if len(SERVICE_JSON) > 100 else f"SERVICE_JSON value: {SERVICE_JSON}")
    print("Please check your GOOGLE_SERVICE_JSON environment variable.")
    raise

client = gspread.authorize(creds)

def get_ws(tab: str):
    return client.open(SHEET_NAME).worksheet(tab)

def _parse_dt(date_str: str, time_str: str) -> datetime | None:
    """Parse date and time strings into a timezone-aware datetime object."""
    try:
        d = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        t = datetime.strptime(time_str.strip(), "%H:%M").time()
        return datetime.combine(d, t, tzinfo=TZ)
    except Exception:
        return None

def get_next_event():
    """Get the nearest upcoming event from the Events sheet."""
    ws = get_ws("Events")
    rows = ws.get_all_records()
    if not rows:
        return None
    
    now = datetime.now(TZ)
    upcoming = []
    
    for r in rows:
        dt = _parse_dt(str(r.get("date", "")).strip(), str(r.get("time", "")).strip())
        if dt and dt >= now:
            upcoming.append((dt, r))
    
    if not upcoming:
        return None
    
    # Sort by datetime and return the nearest upcoming event
    upcoming.sort(key=lambda x: x[0])
    return upcoming[0][1]

def get_template(key: str) -> str | None:
    """Get template URL by key from Templates sheet."""
    ws = get_ws("Templates")
    data = ws.get_all_records()
    for row in data:
        if str(row.get("key", "")).strip().lower() == key.lower():
            return row.get("url")
    return None

def get_categories():
    """Get list of available categories from the Recognition-Categories sheet."""
    try:
        ws = get_ws("Recognition-Categories")
        
        # Get all values from column A (first column)
        categories = ws.col_values(1)
        
        # Remove empty strings and strip whitespace
        categories = [cat.strip() for cat in categories if cat.strip()]
        
        # Remove header if it exists (first row might be a header)
        if categories and categories[0].lower() in ['category', 'categories', 'name']:
            categories = categories[1:]
        
        return categories
    except Exception as e:
        print(f"Error getting categories from Recognition-Categories sheet: {e}")
        # Return empty list if sheet doesn't exist or has issues
        return []

def add_recognition(upline, downline, category, month, remarks):
    """Add a recognition entry to the Recognitions sheet."""
    try:
        ws = get_ws("Recognitions")
        ws.append_row([upline, downline, category, month, remarks])
    except Exception as e:
        print(f"Error in add_recognition: {e}")
        raise

def get_recognitions(month=None, category=None):
    """Get recognition entries, optionally filtered by month and/or category."""
    try:
        ws = get_ws("Recognitions")
        # Get all data from the sheet
        all_data = ws.get_all_values()
        
        if not all_data:
            return []
        
        # Skip header row if it exists
        data = all_data[1:] if len(all_data) > 1 and all_data[0] else all_data
        
        # Filter by month and/or category if specified
        filtered_data = []
        for row in data:
            if len(row) >= 5:  # Ensure we have all required columns
                row_month = row[3].strip() if len(row) > 3 else ""
                row_category = row[2].strip() if len(row) > 2 else ""
                
                # Apply filters
                month_match = not month or row_month.lower() == month.lower()
                category_match = not category or row_category.lower() == category.lower()
                
                if month_match and category_match:
                    filtered_data.append({
                        'upline': row[0] if len(row) > 0 else "",
                        'downline': row[1] if len(row) > 1 else "",
                        'category': row_category,
                        'month': row_month,
                        'remarks': row[4] if len(row) > 4 else ""
                    })
        
        return filtered_data
    except Exception as e:
        print(f"Error getting recognitions: {e}")
        return []

def get_available_months():
    """Get list of unique months from recognitions."""
    try:
        ws = get_ws("Recognitions")
        all_data = ws.get_all_values()
        
        if not all_data:
            return []
        
        # Skip header row if it exists
        data = all_data[1:] if len(all_data) > 1 and all_data[0] else all_data
        
        months = set()
        for row in data:
            if len(row) > 3 and row[3].strip():
                months.add(row[3].strip())
        
        return sorted(list(months))
    except Exception as e:
        print(f"Error getting available months: {e}")
        return []

def get_user_roles() -> tuple[list[str], list[str], list[str]]:
    """Get user roles from UserRoles sheet.
    
    Returns:
        tuple: (mcs, presenters, impacts) from columns B, C, D respectively
    """
    try:
        ws = get_ws("UserRoles")
        
        # Get values from columns B, C, D (2, 3, 4)
        mcs = ws.col_values(2)  # Column B
        presenters = ws.col_values(3)  # Column C  
        impacts = ws.col_values(4)  # Column D
        
        # Process each list: filter empty, trim, remove duplicates
        def process_role_list(role_list):
            processed = [role.strip() for role in role_list if role.strip()]
            # Remove header if present
            if processed and processed[0].lower() in ['mc', 'mcs', 'presenter', 'presenters', 'impact', 'impacts', 'impact speaker', 'impact speakers']:
                processed = processed[1:]
            return list(set(processed))  # Remove duplicates
        
        mcs_processed = process_role_list(mcs)
        presenters_processed = process_role_list(presenters)
        impacts_processed = process_role_list(impacts)
        
        print(f"User roles - MCs: {mcs_processed}, Presenters: {presenters_processed}, Impacts: {impacts_processed}")
        return mcs_processed, presenters_processed, impacts_processed
        
    except Exception as e:
        print(f"Error getting user roles from UserRoles sheet: {e}")
        return [], [], []

def get_event_types() -> list[str]:
    """Get list of event types from the EventTypes sheet.
    
    Returns:
        list[str]: List of event types from column A
        
    Raises:
        ValueError: If no event types are found
    """
    try:
        ws = get_ws("EventTypes")
        # Get all values from column A (first column)
        event_types = ws.col_values(1)
        print(f"Raw event types from sheet: {event_types}")
        # Filter out empty values and skip header if present
        event_types = [event_type.strip() for event_type in event_types if event_type.strip()]
        # Remove header if it exists (first row might be a header)
        if event_types and event_types[0].lower() in ['event type', 'event types', 'type', 'name']:
            event_types = event_types[1:]
        
        if not event_types:
            raise ValueError("No event types found in EventTypes sheet. Please add event types to column A.")
            
        print(f"Processed event types: {event_types}")
        return event_types
    except Exception as e:
        print(f"Error getting event types from EventTypes sheet: {e}")
        if "No event types found" in str(e):
            raise
        return []

def list_upcoming_events(limit_days: int) -> list[tuple[int, dict]]:
    """Get upcoming events within the specified number of days.
    
    Args:
        limit_days: Number of days from today to include
        
    Returns:
        list[tuple[int, dict]]: List of (row_index, event_dict) tuples
    """
    try:
        ws = get_ws("Events")
        all_data = ws.get_all_values()
        
        if not all_data:
            return []
        
        # Skip header row
        data = all_data[1:] if len(all_data) > 1 else []
        
        today = datetime.now(TZ).date()
        end_date = today + timedelta(days=limit_days)
        
        upcoming_events = []
        
        for i, row in enumerate(data, start=2):  # Start from row 2 (1-based, including header)
            if len(row) < 2:  # Need at least type and date
                continue
                
            try:
                event_date = datetime.strptime(row[1].strip(), "%Y-%m-%d").date()
                if today <= event_date <= end_date:
                    event_dict = {
                        'type': row[0] if len(row) > 0 else '',
                        'date': row[1] if len(row) > 1 else '',
                        'time': row[2] if len(row) > 2 else '',
                        'zoom_link': row[3] if len(row) > 3 else '',
                        'mc': row[4] if len(row) > 4 else '',
                        'presenter': row[5] if len(row) > 5 else '',
                        'impact': row[6] if len(row) > 6 else '',
                        'status': row[7] if len(row) > 7 else '',
                        'notes': row[8] if len(row) > 8 else ''
                    }
                    upcoming_events.append((i, event_dict))
            except ValueError:
                # Skip invalid date format
                continue
        
        # Sort by date and time
        upcoming_events.sort(key=lambda x: (x[1]['date'], x[1]['time']))
        return upcoming_events
        
    except Exception as e:
        print(f"Error listing upcoming events: {e}")
        return []

def get_next_event() -> dict | None:
    """Get the nearest upcoming event.
    
    Returns:
        dict | None: Event dictionary or None if no upcoming events
    """
    try:
        ws = get_ws("Events")
        all_data = ws.get_all_values()
        
        if not all_data:
            return None
        
        # Skip header row
        data = all_data[1:] if len(all_data) > 1 else []
        
        now = datetime.now(TZ)
        upcoming_events = []
        
        for row in data:
            if len(row) < 3:  # Need type, date, time
                continue
                
            try:
                event_date = datetime.strptime(row[1].strip(), "%Y-%m-%d").date()
                event_time = datetime.strptime(row[2].strip(), "%H:%M").time()
                event_datetime = datetime.combine(event_date, event_time, tzinfo=TZ)
                
                if event_datetime >= now:
                    event_dict = {
                        'type': row[0] if len(row) > 0 else '',
                        'date': row[1] if len(row) > 1 else '',
                        'time': row[2] if len(row) > 2 else '',
                        'zoom_link': row[3] if len(row) > 3 else '',
                        'mc': row[4] if len(row) > 4 else '',
                        'presenter': row[5] if len(row) > 5 else '',
                        'impact': row[6] if len(row) > 6 else '',
                        'status': row[7] if len(row) > 7 else '',
                        'notes': row[8] if len(row) > 8 else ''
                    }
                    upcoming_events.append((event_datetime, event_dict))
            except ValueError:
                # Skip invalid date/time format
                continue
        
        if not upcoming_events:
            return None
        
        # Sort by datetime and return the nearest
        upcoming_events.sort(key=lambda x: x[0])
        return upcoming_events[0][1]
        
    except Exception as e:
        print(f"Error getting next event: {e}")
        return None

def update_event_roles(event_row_index: int, mc: str | None = None, presenter: str | None = None, impacts: list[str] | None = None) -> None:
    """Update event roles for a specific row.
    
    Args:
        event_row_index: 1-based row index (including header)
        mc: MC name to set (None to skip)
        presenter: Presenter name to set (None to skip)
        impacts: List of impact speaker names (None to skip)
    """
    try:
        ws = get_ws("Events")
        
        # Update MC (column E, index 4)
        if mc is not None:
            ws.update_cell(event_row_index, 5, mc)
        
        # Update Presenter (column F, index 5)
        if presenter is not None:
            ws.update_cell(event_row_index, 6, presenter)
        
        # Update Impact (column G, index 6)
        if impacts is not None:
            impact_str = ", ".join(impacts) if impacts else ""
            ws.update_cell(event_row_index, 7, impact_str)
            
        print(f"Updated event roles for row {event_row_index}: MC={mc}, Presenter={presenter}, Impacts={impacts}")
        
    except Exception as e:
        print(f"Error updating event roles: {e}")
        raise

def list_events_for_date(target_date: date) -> list[dict]:
    """Get all events for a specific date.
    
    Args:
        target_date: Date to search for (date object)
        
    Returns:
        list[dict]: List of event dictionaries for the date
    """
    try:
        ws = get_ws("Events")
        all_data = ws.get_all_values()
        
        if not all_data:
            return []
        
        # Skip header row
        data = all_data[1:] if len(all_data) > 1 else []
        
        events_for_date = []
        
        for row in data:
            if len(row) < 2:  # Need at least type and date
                continue
                
            try:
                event_date = datetime.strptime(row[1].strip(), "%Y-%m-%d").date()
                if event_date == target_date:
                    event_dict = {
                        'type': row[0] if len(row) > 0 else '',
                        'date': row[1] if len(row) > 1 else '',
                        'time': row[2] if len(row) > 2 else '',
                        'zoom_link': row[3] if len(row) > 3 else '',
                        'mc': row[4] if len(row) > 4 else '',
                        'presenter': row[5] if len(row) > 5 else '',
                        'impact': row[6] if len(row) > 6 else '',
                        'status': row[7] if len(row) > 7 else '',
                        'notes': row[8] if len(row) > 8 else ''
                    }
                    events_for_date.append(event_dict)
            except ValueError:
                # Skip invalid date format
                continue
        
        # Sort by time
        events_for_date.sort(key=lambda x: x['time'])
        return events_for_date
        
    except Exception as e:
        print(f"Error listing events for date {target_date}: {e}")
        return []
