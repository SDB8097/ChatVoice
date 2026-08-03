import asyncio
import os
import tempfile
import uuid
import logging

import edge_tts
import pygame


class EdgeTTS:

    def __init__(self, config: dict):

        self.voice = config["voice"]["default_voice"]
        self.rate = config["voice"]["rate"]
        self.pitch = config["voice"]["pitch"]
        self.volume = config["voice"]["volume"]

        self.audio_available = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.audio_available = True

        except Exception as e:
            # Running in headless environment or no audio device
            logging.warning(f"pygame.mixer init failed: {e}")
            self.audio_available = False

    async def speak(self, text: str):

        if not text or not text.strip():
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

        try:
            await communicate.save(filename)

            if not self.audio_available:
                logging.warning("Аудио недоступно, файл сохранён, но воспроизведение пропущено: %s", filename)
                try:
                    os.remove(filename)
                except Exception:
                    pass
                return

            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.05)

                try:
                    pygame.mixer.music.unload()
                except Exception:
                    pass

            except Exception as e:
                logging.exception(e)

        finally:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception:
                pass

    async def speak_user(self, username: str, message: str):

        text = f"{username} говорит. {message}"

        await self.speak(text)

    async def test(self):

        await self.speak("Проверка озвучки прошла успешно.")
