import asyncio
import logging
from typing import Optional

from tts.edge import EdgeTTS


class TTSQueue:

    def __init__(self, config: dict):

        self.config = config

        self.tts = EdgeTTS(config)

        self.queue: asyncio.Queue = asyncio.Queue(
            maxsize=config["queue"]["max_size"]
        )

        self.worker_task: Optional[asyncio.Task] = None

        self.running = False

    # ---------------------------------------------------------

    async def start(self):

        if self.running:
            return

        self.running = True

        self.worker_task = asyncio.create_task(
            self.worker()
        )

        logging.info("TTS Queue запущена.")

    # ---------------------------------------------------------

    async def stop(self):

        self.running = False

        if self.worker_task:

            self.worker_task.cancel()

            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

        logging.info("TTS Queue остановлена.")

    # ---------------------------------------------------------

    async def add(self, username: str, message: str):

        if not self.running:
            return

        if self.queue.full():

            logging.warning("Очередь TTS заполнена.")

            if self.config["queue"]["skip_if_busy"]:
                return

        await self.queue.put(
            (
                username,
                message
            )
        )

    # ---------------------------------------------------------

    async def worker(self):

        delay = self.config["queue"]["min_delay"]

        while self.running:

            try:

                username, message = await self.queue.get()

                await self.tts.speak_user(
                    username,
                    message
                )

                await asyncio.sleep(delay)

            except asyncio.CancelledError:

                break

            except Exception as error:

                logging.exception(error)

    # ---------------------------------------------------------

    def size(self):

        return self.queue.qsize()

    # ---------------------------------------------------------

    def clear(self):

        while not self.queue.empty():

            try:
                self.queue.get_nowait()
                self.queue.task_done()

            except Exception:
                break