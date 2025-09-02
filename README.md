# Zoom Impact Telegram Bot

A Telegram bot for the Zoom Impact Group that integrates with Google Sheets for event management, recognition tracking, and template sharing.

## Features

- **Event Management**: View upcoming events with automatic date sorting
- **Recognition System**: Add and track team recognitions
- **Template Sharing**: Access slides and guidelines
- **Role-based Access**: Admin and member roles with different permissions
- **Google Sheets Integration**: All data stored in Google Sheets

## Bot Commands

- `/menu` - Show main menu with role-based options
- `/rec Upline | Downline | Category | Month | Remarks` - Add a recognition entry

## Google Sheets Schema

The bot expects a Google Sheet with the following tabs:

### Events Tab
Columns: `type`, `date`, `time`, `zoom_link`, `mc`, `impact`, `status`, `notes`
- `date`: Format YYYY-MM-DD
- `time`: Format HH:MM (24-hour)

### Recognitions Tab
Columns: `upline`, `downline`, `category`, `month`, `remarks`

### Templates Tab
Columns: `key`, `url`
- Keys: `slides`, `guidelines`

## Setup

### Prerequisites

1. Python 3.10 or higher
2. Google Cloud Service Account with Sheets API access
3. Telegram Bot Token from [@BotFather](https://t.me/botfather)

### Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Create Service Account
   - Download the JSON key file
5. Share your Google Sheet with the service account email (Editor permissions)

### Installation

#### Option 1: Using pipx (Recommended)

```bash
# Install the bot
pipx install .

# Set environment variables
export BOT_TOKEN="your_telegram_bot_token"
export GOOGLE_SERVICE_JSON="service_account.json"
export SHEET_NAME="Zoom Impact Bot Data"

# Run the bot
zoom-impact-bot
```

#### Option 2: Using virtual environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN="your_telegram_bot_token"
export GOOGLE_SERVICE_JSON="service_account.json"
export SHEET_NAME="Zoom Impact Bot Data"

# Run the bot
python bot.py
```

### Environment Variables

Create a `.env` file or set environment variables:

```bash
BOT_TOKEN=123456:ABC-DEF...
GOOGLE_SERVICE_JSON=service_account.json
SHEET_NAME=Zoom Impact Bot Data
```

- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `GOOGLE_SERVICE_JSON`: Path to your Google service account JSON file
- `SHEET_NAME`: Name of your Google Sheet

## Usage

1. Start the bot using one of the installation methods above
2. Find your bot on Telegram and send `/menu`
3. Use the inline keyboard to navigate features:
   - **Next**: View the next upcoming event
   - **Slides**: Get latest slides link
   - **Guidelines**: Get guidelines link
   - **Recognition**: Instructions for adding recognitions

## Development

### Project Structure

```
zoom-impact-bot/
├── zoom_impact_bot/          # Main package
│   ├── cli.py               # CLI entry point
│   ├── run.py               # Bot main logic
│   ├── sheets.py            # Google Sheets integration
│   └── commands/            # Command handlers
│       ├── events.py        # Event-related commands
│       ├── recognition.py   # Recognition commands
│       ├── templates.py     # Template commands
│       └── utils.py         # Utility functions
├── pyproject.toml           # Package configuration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Adding New Features

1. Create new command handlers in `zoom_impact_bot/commands/`
2. Register handlers in `zoom_impact_bot/run.py`
3. Update `utils.py` for new menu items if needed

## Troubleshooting

### Common Issues

1. **"BOT_TOKEN is not set"**: Make sure you've set the BOT_TOKEN environment variable
2. **Google Sheets access denied**: Ensure the service account email has Editor access to your sheet
3. **No upcoming events**: Check that your Events tab has properly formatted date/time columns

### Logs

The bot logs startup information including:
- Loaded sheet name
- Current timezone (Asia/Kolkata)
- Any authentication errors

## Railway Deployment

### Prerequisites for Railway

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to GitHub
3. **Google Service Account**: You'll need the JSON key file content

### Deploy to Railway

1. **Connect GitHub**:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Set Environment Variables**:
   In Railway dashboard, go to your project → Variables tab and add:
   ```
   BOT_TOKEN=your_telegram_bot_token
   GOOGLE_SERVICE_JSON={"type":"service_account","project_id":"..."}
   SHEET_NAME=Zoom Impact Bot Data
   ```

3. **Deploy**:
   - Railway will automatically detect the Python project
   - It will install dependencies from `requirements.txt`
   - The bot will start using `python start.py`

### Environment Variables for Railway

- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `GOOGLE_SERVICE_JSON`: The **entire JSON content** of your service account file (not file path)
- `SHEET_NAME`: Name of your Google Sheet (optional, defaults to "Zoom Impact Bot Data")

### Important Notes for Railway

- **Service Account JSON**: Paste the entire JSON content as the `GOOGLE_SERVICE_JSON` environment variable
- **No File Paths**: Railway doesn't support local file paths, so we use environment variables
- **Automatic Restarts**: Railway will restart the bot if it crashes
- **Logs**: Check Railway dashboard for bot logs and status

### Local Testing Before Deployment

```bash
# Test with environment variables (like Railway will use)
export BOT_TOKEN="your_token"
export GOOGLE_SERVICE_JSON='{"type":"service_account",...}'  # Full JSON content
export SHEET_NAME="Zoom Impact Bot Data"
python start.py
```

## License

This project is for internal use by the Zoom Impact Group.