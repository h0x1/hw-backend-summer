import asyncio
from asyncio import Task
from typing import Optional

from app.store import Store


class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None

    async def start(self):
        self.is_running = True
        asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False

    async def poll(self):
        while self.is_running:
            updates = await self.store.vk_api.poll()
            await self.store.bots_manager.handle_updates(updates)
