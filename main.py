import asyncio
import json
import logging
import threading
import sys
from pathlib import Path

from gui.window import ChatVoiceApp
from chat.manager import ChatManager
from tts.queue import TTSQueue
from filters.text import TextFilter
from filters.spam import SpamFilter


CONFIG_FILE = "config.json"


class ChatVoice:

    def __init__(self):

        self.config = self.load_config()

        self.setup_logging()

        self.loop = asyncio.new_event_loop()

        self.loop_thread = threading.Thread(
            target=self.run_loop,
            daemon=True
        )

        self.loop_thread.start()

        self.tts = TTSQueue(self.config)

        self.text_filter = TextFilter(self.config)

        self.spam_filter = SpamFilter(self.config)

        self.manager = ChatManager(
            self.config,
            self.on_chat_message
        )

        self.gui = ChatVoiceApp(
            self.config
        )

        self.gui.set_callbacks(
            on_start=self.start,
            on_stop=self.stop
        )

    # -------------------------------------------------

    def load_config(self):

        path = Path(CONFIG_FILE)

        if not path.exists():
            raise FileNotFoundError(
                CONFIG_FILE
            )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # -------------------------------------------------

    def setup_logging(self):

        level = self.config["app"].get(
            "log_level",
            "INFO"
        )

        logging.basicConfig(
            level=getattr(logging, level),
            format="[%(levelname)s] %(message)s"
        )

    # -------------------------------------------------

    def run_loop(self):

        asyncio.set_event_loop(self.loop)

        self.loop.run_forever()

    # -------------------------------------------------

    def start(self):

        self.config["youtube"]["url"] = (
            self.gui.get_youtube_url()
        )

        self.config["voice"]["default_voice"] = (
            self.gui.get_selected_voice()
        )

        asyncio.run_coroutine_threadsafe(
            self.async_start(),
            self.loop
        )

    # -------------------------------------------------

    def stop(self):

        asyncio.run_coroutine_threadsafe(
            self.async_stop(),
            self.loop
        )

    # -------------------------------------------------

    async def async_start(self):

        self.gui.log(
            "Запуск..."
        )

        await self.tts.start()

        await self.manager.start()

        self.gui.log(
            "Подключено."
        )

    # -------------------------------------------------

    async def async_stop(self):

        self.gui.log(
            "Остановка..."
        )

        await self.manager.stop()

        await self.tts.stop()

        self.gui.log(
            "Остановлено."
        )

    # -------------------------------------------------

    def on_chat_message(
        self,
        data
    ):

        username = data.get(
            "username",
            ""
        )

        message = data.get(
            "message",
            ""
        )

        message = self.text_filter.process(
            username,
            message
        )

        if message is None:
            return

        if not self.spam_filter.check(
            username,
            message
        ):
            return

        self.gui.log(
            f"[{username}] {message}"
        )

        asyncio.run_coroutine_threadsafe(
            self.tts.add(
                username,
                message
            ),
            self.loop
        )
            # -------------------------------------------------

    def run(self):

        try:

            self.gui.run()

        finally:

            future = asyncio.run_coroutine_threadsafe(
                self.async_stop(),
                self.loop
            )

            try:
                future.result(timeout=5)
            except Exception:
                pass

            self.loop.call_soon_threadsafe(
                self.loop.stop
            )

            self.loop_thread.join(timeout=5)

    # -------------------------------------------------

    def shutdown(self):

        try:

            future = asyncio.run_coroutine_threadsafe(
                self.async_stop(),
                self.loop
            )

            future.result(timeout=5)

        except Exception as error:

            logging.exception(error)

        finally:

            self.loop.call_soon_threadsafe(
                self.loop.stop
            )


# =====================================================


def main():

    try:

        app = ChatVoice()

        app.run()

    except KeyboardInterrupt:

        pass

    except Exception as error:

        logging.exception(error)

        sys.exit(1)


# =====================================================

if __name__ == "__main__":

    main()