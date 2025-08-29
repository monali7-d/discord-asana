import discord
import asyncio
from tools.asana import create_asana_task
from persistence.store import IdempotencyStore
from datetime import datetime, timedelta, timezone
from discord import ChannelType

class CatchupClient(discord.Client):
    def __init__(self, *, target_channels, monali_user_id, asana_pat, asana_project_gid, after_time, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(intents=intents, **kwargs)
        self.target_channels = set(target_channels)
        self.monali_user_id = monali_user_id
        self.asana_pat = asana_pat
        self.asana_project_gid = asana_project_gid
        self.after_time = after_time
        self.idempotency_store = IdempotencyStore()

    async def on_ready(self):
        print(f'[CATCHUP] Logged in as {self.user} (ID: {self.user.id})')
        # Kick off the catch-up work and then close the client when finished
        asyncio.create_task(self._run_catchup_and_close())

    async def _run_catchup_and_close(self):
        try:
            await self._process_channels()
        finally:
            await self.close()

    async def _process_channels(self):
        for channel_id in self.target_channels:
            print(f'[CATCHUP] Attempting to fetch channel: {channel_id}')
            try:
                channel = await self.fetch_channel(int(channel_id))
                print(f'[CATCHUP] Successfully fetched channel {channel_id}')
                count_total = 0
                count_skipped = 0
                count_processed = 0
                async for message in channel.history(after=self.after_time, oldest_first=True):
                    count_total += 1
                    print(f'[CATCHUP] Fetched message: id={message.id}, author={message.author}, content={message.content[:60]}, channel_type={getattr(message.channel, "type", None)}')
                    if message.guild is None:
                        print(f'[CATCHUP] Skipped: Not in a guild.')
                        count_skipped += 1
                        continue
                    if str(message.author.id) == self.monali_user_id:
                        print(f'[CATCHUP] Skipped: From excluded user {self.monali_user_id}.')
                        count_skipped += 1
                        continue
                    if message.reference is not None:
                        print(f'[CATCHUP] Skipped: Is a reply (has message_reference).')
                        count_skipped += 1
                        continue
                    if hasattr(message.channel, 'type') and message.channel.type in [ChannelType.public_thread, ChannelType.private_thread]:
                        if message.id != message.channel.id:
                            print(f'[CATCHUP] Skipped: Not the starter message in thread.')
                            count_skipped += 1
                            continue
                    if await self.idempotency_store.is_processed(message.id):
                        print(f'[CATCHUP] Skipped: Already processed (idempotency).')
                        count_skipped += 1
                        continue
                    event = {
                        'message_id': str(message.id),
                        'author': str(message.author),
                        'content': message.content,
                        'permalink': f'https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}'
                    }
                    print(f'[CATCHUP] Processing event: {event}')
                    await create_asana_task(event, self.asana_pat, self.asana_project_gid)
                    await self.idempotency_store.mark_processed(message.id)
                    count_processed += 1
                print(f'[CATCHUP] Channel {channel_id}: Total={count_total}, Skipped={count_skipped}, Processed={count_processed}')
            except Exception as e:
                print(f'[CATCHUP] Error fetching or processing channel {channel_id}: {e}')

async def run_catchup(discord_token, asana_pat, asana_project_gid, target_channels, monali_user_id):
    print('[CATCHUP] Scanning only messages from the last 72 hours in each channel.')
    print(f'[CATCHUP] TARGET_CHANNELS: {target_channels}')
    now = datetime.now(timezone.utc)
    after_time = now - timedelta(hours=72)
    client = CatchupClient(
        target_channels=target_channels,
        monali_user_id=monali_user_id,
        asana_pat=asana_pat,
        asana_project_gid=asana_project_gid,
        after_time=after_time
    )
    # start() will block until we call client.close() from inside _run_catchup_and_close
    await client.start(discord_token, reconnect=False)
