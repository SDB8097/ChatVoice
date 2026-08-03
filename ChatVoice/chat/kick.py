import asyncio
import logging
from typing import Callable, Optional

import aiohttp


class KickChat:

    def __init__(self, config: dict, callback: Callable[[dict], None]):

        self.config = config
        self.callback = callback

        self.running = False

        self.channel: str = config["kick"].get("channel", "")

        self.channel_id: Optional[int] = None

        self.session: Optional[aiohttp.ClientSession] = None

    # ---------------------------------------------------------

    async def run(self):

        if not self.channel:

            logging.warning("Kick канал не указан.")

            return

        self.running = True

        self.session = aiohttp.ClientSession()

        try:

            self.channel_id = await self.get_channel_id()

            if self.channel_id is None:

                logging.error("Не удалось получить ID канала Kick.")

                return

            logging.info(
                f"Kick подключен к каналу: {self.channel}"
            )

            while self.running:

                messages = await self.get_messages()

                for message in messages:

                    data = {

                        "platform": "kick",

                        "username": message["username"],

                        "message": message["message"],

                        "id": message["id"],

                        "timestamp": message["timestamp"]
                    }

                    self.callback(data)

                await asyncio.sleep(1)

        except Exception as error:

            logging.exception(error)

        finally:

            await self.stop()

    # ---------------------------------------------------------

    async def stop(self):

        self.running = False

        if self.session:

            await self.session.close()

        logging.info("Kick остановлен.")

    # ---------------------------------------------------------

    async def get_channel_id(self) -> Optional[int]:

        url = f"https://kick.com/api/v2/channels/{self.channel}"

        async with self.session.get(url) as response:

            if response.status != 200:
                return None

            data = await response.json()

            return data.get("id")

    # ---------------------------------------------------------

    async def get_messages(self):

        """
        ВРЕМЕННАЯ ЗАГЛУШКА.

        Здесь позже будет подключение к WebSocket Kick.

        Пока возвращает пустой список.
        """

        return []