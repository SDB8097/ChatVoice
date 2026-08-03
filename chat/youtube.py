import asyncio
import logging
from typing import Callable

from chat_downloader import ChatDownloader


class YouTubeChat:

    def __init__(self, config: dict, callback: Callable[[dict], None]):

        self.config = config
        self.callback = callback

        self.running = False

        self.chat = None

    async def run(self):

        self.running = True

        url = self.config["youtube"]["url"]

        if not url:
            logging.warning("YouTube URL пустой.")
            return

        try:

            self.chat = ChatDownloader().get_chat(url)

            logging.info("YouTube чат подключен.")

            while self.running:

                try:

                    message = next(self.chat)

                except StopIteration:
                    break

                except Exception as error:
                    logging.exception(error)
                    await asyncio.sleep(1)
                    continue

                data = {
                    "platform": "youtube",
                    "username": message.get("author", {}).get("name", "Unknown"),
                    "message": message.get("message", ""),
                    "id": message.get("message_id", ""),
                    "timestamp": message.get("timestamp", 0)
                }

                self.callback(data)

                await asyncio.sleep(0)

        except Exception as error:

            logging.exception(error)

        finally:

            logging.info("YouTube чат остановлен.")

    async def stop(self):

        self.running = False