import aiosqlite
import asyncio
import os

class IdempotencyStore:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), 'idempotency.sqlite3')
        self._initialized = False

    async def _init_db(self):
        if self._initialized:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS processed_messages (
                message_id TEXT PRIMARY KEY
            )''')
            await db.commit()
        self._initialized = True

    async def is_processed(self, message_id):
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT 1 FROM processed_messages WHERE message_id = ?', (str(message_id),)) as cursor:
                return await cursor.fetchone() is not None

    async def mark_processed(self, message_id):
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT OR IGNORE INTO processed_messages (message_id) VALUES (?)', (str(message_id),))
            await db.commit()
