import os
import asyncio
from dotenv import load_dotenv
import discord
from discord import ChannelType

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_CHANNELS = os.getenv('TARGET_CHANNELS', '').split(',')

class ChannelTestClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        for channel_id in TARGET_CHANNELS:
            try:
                print(f'Attempting to fetch channel: {channel_id}')
                channel = await self.fetch_channel(int(channel_id))
                print(f'Success: Channel {channel_id} is named \"{channel.name}\" and type {channel.type}')
            except Exception as e:
                print(f'Error fetching channel {channel_id}: {e}')
        await self.close()

if __name__ == '__main__':
    intents = discord.Intents.default()
    client = ChannelTestClient(intents=intents)
    asyncio.run(client.start(DISCORD_BOT_TOKEN))