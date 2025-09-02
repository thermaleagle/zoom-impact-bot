import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
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

def add_recognition(upline, downline, category, month, remarks):
    """Add a recognition entry to the Recognitions sheet."""
    try:
        print(f"Adding recognition: {[upline, downline, category, month, remarks]}")
        ws = get_ws("Recognitions")
        print(f"Got worksheet: {ws.title}")
        ws.append_row([upline, downline, category, month, remarks])
        print("Recognition added successfully")
    except Exception as e:
        print(f"Error in add_recognition: {e}")
        raise
