import asyncio
import logging
from typing import Callable

try:
    from twitchAPI.chat import Chat
    from twitchAPI.twitch import Twitch
    from twitchAPI.type import AuthScope, ChatEvent
except ImportError:
    Chat = None
    Twitch = None


class TwitchChat:

    def __init__(self, config: dict, callback: Callable[[dict], None]):

        self.config = config
        self.callback = callback

        self.running = False

        self.chat = None
        self.twitch = None

    # ---------------------------------------------------------

    async def run(self):

        if Chat is None:

            logging.warning(
                "twitchAPI не установлен."
            )

            return

        client_id = self.config["twitch"].get("client_id", "")
        client_secret = self.config["twitch"].get("client_secret", "")
        channel = self.config["twitch"].get("channel", "")

        if not client_id or not client_secret or not channel:

            logging.warning(
                "Twitch не настроен."
            )

            return

        self.running = True

        try:

            self.twitch = await Twitch(client_id, client_secret)

            await self.twitch.authenticate_app(
                [AuthScope.CHAT_READ]
            )

            self.chat = await Chat(self.twitch)

            @self.chat.event(ChatEvent.MESSAGE)
            async def on_message(message):

                if not self.running:
                    return

                data = {
                    "platform": "twitch",
                    "username": message.user.name,
                    "message": message.text,
                    "id": "",
                    "timestamp": 0
                }

                self.callback(data)

            self.chat.start()

            await self.chat.join_room(channel)

            logging.info(
                f"Twitch подключен: {channel}"
            )

            while self.running:

                await asyncio.sleep(1)

        except Exception as error:

            logging.exception(error)

        finally:

            await self.stop()

    # ---------------------------------------------------------

    async def stop(self):

        self.running = False

        try:

            if self.chat:

                self.chat.stop()

        except Exception:

            pass

        try:

            if self.twitch:

                await self.twitch.close()

        except Exception:

            pass

        logging.info("Twitch остановлен.")