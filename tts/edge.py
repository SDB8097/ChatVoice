import asyncio
import os
import tempfile
import uuid

import edge_tts
import pygame


class EdgeTTS:

    def __init__(self, config: dict):

        self.voice = config["voice"]["default_voice"]
        self.rate = config["voice"]["rate"]
        self.pitch = config["voice"]["pitch"]
        self.volume = config["voice"]["volume"]

        if not pygame.mixer.get_init():
            pygame.mixer.init()

    async def speak(self, text: str):

        if not text.strip():
            return

        filename = os.path.join(
            tempfile.gettempdir(),
            f"{uuid.uuid4()}.mp3"
        )

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch,
            volume=self.volume
        )

        await communicate.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)

        pygame.mixer.music.unload()

        try:
            os.remove(filename)
        except Exception:
            pass

    async def speak_user(self, username: str, message: str):

        text = f"{username} говорит. {message}"

        await self.speak(text)

    async def test(self):

        await self.speak("Проверка озвучки прошла успешно.")