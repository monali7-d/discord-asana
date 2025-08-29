import os
import asyncio
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
ASANA_PAT = os.getenv('ASANA_PAT')
ASANA_PROJECT_GID = os.getenv('ASANA_PROJECT_GID')
TARGET_CHANNELS = os.getenv('TARGET_CHANNELS', '').split(',')
MONALI_USER_ID = os.getenv('MONALI_USER_ID')

async def main():
    parser = argparse.ArgumentParser(description='Discord-Asana Agno Agent')
    parser.add_argument('--catchup', action='store_true', help='Run in catch-up mode (batch sync)')
    args = parser.parse_args()

    if args.catchup:
        from bot.catchup import run_catchup
        await run_catchup(
            discord_token=DISCORD_BOT_TOKEN,
            asana_pat=ASANA_PAT,
            asana_project_gid=ASANA_PROJECT_GID,
            target_channels=TARGET_CHANNELS,
            monali_user_id=MONALI_USER_ID
        )
    else:
        from bot.agent import start_agent
        await start_agent(
            discord_token=DISCORD_BOT_TOKEN,
            asana_pat=ASANA_PAT,
            asana_project_gid=ASANA_PROJECT_GID,
            target_channels=TARGET_CHANNELS,
            monali_user_id=MONALI_USER_ID
        )

if __name__ == '__main__':
    asyncio.run(main())
