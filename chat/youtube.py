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

            # Получение итератора может быть блокирующим, выполняем в отдельном потоке
            self.chat = await asyncio.to_thread(lambda: ChatDownloader().get_chat(url))

            logging.info("YouTube чат подключен.")

            while self.running:

                try:

                    # next() над итератором chat_downloader может блокировать,
                    # поэтому вызываем его в отдельном потоке через asyncio.to_thread
                    message = await asyncio.to_thread(next, self.chat)

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

                # callback будет вызываться из асинхронного потока; GUI обновления
                # должны быть безопасно запланированы в GUI-потоке (см. gui.log)
                self.callback(data)

                await asyncio.sleep(0)

        except Exception as error:

            logging.exception(error)

        finally:

            logging.info("YouTube чат остановлен.")

    async def stop(self):

        self.running = False
