import customtkinter as ctk
import logging


class ChatVoiceApp:

    def __init__(self, config: dict):

        self.config = config

        ctk.set_appearance_mode(
            config["app"].get("theme", "dark")
        )

        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()

        self.root.title(
            f'{config["app"]["name"]} {config["app"]["version"]}'
        )

        self.root.geometry("900x650")
        self.root.minsize(900, 650)

        self.create_widgets()

    # --------------------------------------------------

    def create_widgets(self):

        # -------------------------------
        # Верхняя панель
        # -------------------------------

        self.title_label = ctk.CTkLabel(
            self.root,
            text="ChatVoice",
            font=("Segoe UI", 26, "bold")
        )

        self.title_label.pack(
            pady=(20, 10)
        )

        # -------------------------------
        # YouTube URL
        # -------------------------------

        self.url_label = ctk.CTkLabel(
            self.root,
            text="YouTube Stream URL"
        )

        self.url_label.pack()

        self.url_entry = ctk.CTkEntry(
            self.root,
            width=700
        )

        self.url_entry.pack(
            pady=5
        )

        self.url_entry.insert(
            0,
            self.config["youtube"]["url"]
        )

        # -------------------------------
        # Голос
        # -------------------------------

        self.voice_label = ctk.CTkLabel(
            self.root,
            text="Голос"
        )

        self.voice_label.pack(
            pady=(15, 0)
        )

        self.voice_menu = ctk.CTkOptionMenu(
            self.root,
            values=[
                "ru-RU-DmitryNeural",
                "ru-RU-SvetlanaNeural",
                "en-US-GuyNeural",
                "en-US-JennyNeural"
            ]
        )

        self.voice_menu.pack(
            pady=5
        )

        self.voice_menu.set(
            self.config["voice"]["default_voice"]
        )

        # -------------------------------
        # Лог
        # -------------------------------

        self.log_box = ctk.CTkTextbox(
            self.root,
            width=820,
            height=320
        )

        self.log_box.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True
        )

        self.log("ChatVoice запущен.")
        self.log("Ожидание подключения...")

        # -------------------------------
        # Кнопки
        # -------------------------------

        self.button_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )

        self.button_frame.pack(
            pady=10
        )

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="▶ Подключиться",
            width=180,
            command=self.start_chat
        )

        self.start_button.grid(
            row=0,
            column=0,
            padx=10
        )

        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="■ Стоп",
            width=180,
            fg_color="#B22222",
            hover_color="#8B0000",
            command=self.stop_chat
        )

        self.stop_button.grid(
            row=0,
            column=1,
            padx=10
        )

    # --------------------------------------------------

    def log(self, text: str):

        self.log_box.insert(
            "end",
            text + "\n"
        )

        self.log_box.see("end")

        logging.info(text)

    # --------------------------------------------------

    def start_chat(self):

        url = self.url_entry.get().strip()

        self.log(f"Подключение к: {url}")

    # --------------------------------------------------

    def stop_chat(self):

        self.log("Чат остановлен.")

    # --------------------------------------------------

    def run(self):

        self.root.mainloop()