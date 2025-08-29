# Discord-Asana Agno Agent

A Python-based agent that connects Discord to Asana in real time, creating Asana tasks for new threads in specified Discord channels.

## Features
- Real-time Discord Gateway connection (no polling)
- Filters for specific channels, new threads, and user exclusions
- Idempotency with SQLite/file store
- Asana integration with custom fields and tags
- Configurable via environment variables
- Docker-ready

## Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your values
   - `DISCORD_BOT_TOKEN`
   - `ASANA_PAT`
   - `ASANA_PROJECT_GID`
   - `TARGET_CHANNELS` (comma-separated IDs)
   - `MONALI_USER_ID`
   - Optional: `ASANA_TAG_GIDS` (comma-separated tag GIDs)
   - Optional: `ASANA_DISCORD_MSG_ID_FIELD_GID` (custom field GID)
4. Run the bot realtime: `python main.py`
5. Run catch-up mode: `python main.py --catchup`

## Docker
Build and run with Docker:
```sh
docker build -t discord-asana-agno .
docker run --env-file .env discord-asana-agno
```
