import asyncio
import logging
from typing import Callable, Dict, Optional

from chat.youtube import YouTubeChat


class ChatManager:
    """
    Управляет всеми подключенными чатами.
    """

    def __init__(
        self,
        config: dict,
        message_callback: Callable[[dict], None]
    ):

        self.config = config
        self.message_callback = message_callback

        self.running = False

        self.providers: Dict[str, object] = {}

        self.tasks: Dict[str, asyncio.Task] = {}

    # ---------------------------------------------------------

    async def start(self):

        if self.running:
            return

        self.running = True

        logging.info("Запуск ChatManager")

        if self.config["youtube"]["enabled"]:

            youtube = YouTubeChat(
                self.config,
                self.message_callback
            )

            self.providers["youtube"] = youtube

            self.tasks["youtube"] = asyncio.create_task(
                youtube.run()
            )

        if self.config["twitch"]["enabled"]:
            logging.info("Twitch пока не реализован.")

        if self.config["kick"]["enabled"]:
            logging.info("Kick пока не реализован.")

    # ---------------------------------------------------------

    async def stop(self):

        if not self.running:
            return

        self.running = False

        logging.info("Остановка ChatManager")

        for provider in self.providers.values():

            try:
                await provider.stop()

            except Exception as error:

                logging.exception(error)

        for task in self.tasks.values():

            task.cancel()

        self.providers.clear()

        self.tasks.clear()

    # ---------------------------------------------------------

    async def restart(self):

        await self.stop()

        await self.start()

    # ---------------------------------------------------------

    def is_running(self):

        return self.running

    # ---------------------------------------------------------

    def get_provider(self, name: str) -> Optional[object]:

        return self.providers.get(name)

    # ---------------------------------------------------------

    def provider_count(self):

        return len(self.providers)