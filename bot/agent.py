import discord
import os
from discord import Intents
from tools.asana import create_asana_task
from persistence.store import IdempotencyStore

class DiscordAsanaAgent(discord.Client):
    def __init__(self, *, target_channels, monali_user_id, asana_pat, asana_project_gid, **kwargs):
        intents = Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(intents=intents, **kwargs)
        self.target_channels = set(target_channels)
        self.monali_user_id = monali_user_id
        self.asana_pat = asana_pat
        self.asana_project_gid = asana_project_gid
        self.idempotency_store = IdempotencyStore()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        print(f"Received message: id={message.id}, author={message.author}, channel={message.channel.id}, content={message.content}")
        # Ignore DMs and bot's own messages
        if message.guild is None:
            print("Ignored: Not in a guild.")
            return
        if str(message.author.id) == self.monali_user_id:
            print("Ignored: Message from MONALI_USER_ID.")
            return
        # Only process messages in target channels
        if str(message.channel.id) not in self.target_channels:
            print(f"Ignored: Channel {message.channel.id} not in target channels.")
            return
        # Only process new threads (no message_reference)
        if hasattr(message, 'message_reference') and message.message_reference:
            print("Ignored: Message is a reply (has message_reference).")
            return
        # Idempotency check
        if await self.idempotency_store.is_processed(message.id):
            print(f"Ignored: Message {message.id} already processed.")
            return
        # Normalize event
        event = {
            'message_id': str(message.id),
            'author': str(message.author),
            'content': message.content,
            'permalink': f'https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}'
        }
        print(f"Processing event: {event}")
        # Create Asana task
        await create_asana_task(event, self.asana_pat, self.asana_project_gid)
        await self.idempotency_store.mark_processed(message.id)
        print(f"Marked message {message.id} as processed.")

async def start_agent(discord_token, asana_pat, asana_project_gid, target_channels, monali_user_id):
    client = DiscordAsanaAgent(
        target_channels=target_channels,
        monali_user_id=monali_user_id,
        asana_pat=asana_pat,
        asana_project_gid=asana_project_gid
    )
    await client.start(discord_token)
