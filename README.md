# 🇲🇲 Myanmar CV Builder Bot

A Telegram bot that helps Myanmar job seekers create professional CV/Resume PDFs.

## Features
- 4 beautiful CV templates (Modern, Classic, Creative, Myanmar Traditional)
- AI-powered CV content polishing (OpenRouter)
- Export to PDF, Excel, Google Sheets
- Full conversation in Myanmar language
- Photo upload support

## Setup

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/myanmar-cv-bot
cd myanmar-cv-bot
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Config
Edit `config.json`:
```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "openrouter_key": "YOUR_OPENROUTER_KEY"
}
```

### 4. Run
```bash
python main.py
```

## Deploy on Railway
1. Push to GitHub
2. Connect repo on railway.app
3. Add environment variables: BOT_TOKEN, OPENROUTER_KEY
4. Deploy!

## Bot Commands
- `/start` - Start building CV
- `/template` - Choose template
- `/skip` - Skip optional field
- `/cancel` - Cancel current session
- `/mycvs` - View your previous CVs
- `/stats` - Bot statistics

## Tech Stack
- Python 3.11+
- python-telegram-bot 20.7
- ReportLab (PDF generation)
- OpenRouter AI API
- SQLite database
- openpyxl (Excel export)
