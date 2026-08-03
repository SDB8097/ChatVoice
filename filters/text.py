import re


class TextFilter:

    def __init__(self, config: dict):

        self.config = config["filters"]
        self.blacklist = config["blacklist"]
        self.whitelist = config["whitelist"]
        self.replace = config["replace"]

    # ---------------------------------------------------------

    def process(self, username: str, message: str):

        if not self.is_allowed_user(username):
            return None

        if not message:
            return None

        message = message.strip()

        if self.config["ignore_empty"] and not message:
            return None

        if (
            self.config["ignore_commands"]
            and message.startswith(
                self.config["command_prefix"]
            )
        ):
            return None

        if (
            self.config["ignore_links"]
            and self.contains_link(message)
        ):
            return None

        if (
            self.config["ignore_numbers_only"]
            and message.isdigit()
        ):
            return None

        if len(message) < self.config["min_length"]:
            return None

        if len(message) > self.config["max_length"]:
            message = message[: self.config["max_length"]]

        message = self.replace_words(message)

        if self.config["remove_symbols"]:
            message = self.remove_symbols(message)

        if self.config["remove_emojis"]:
            message = self.remove_emojis(message)

        message = self.limit_letters(message)

        if self.contains_blacklist(message):
            return None

        return message.strip()

    # ---------------------------------------------------------

    def is_allowed_user(self, username: str):

        if self.whitelist["enabled"]:

            return username in self.whitelist["users"]

        return username not in self.blacklist["users"]

    # ---------------------------------------------------------

    def contains_blacklist(self, message: str):

        lower = message.lower()

        for word in self.blacklist["words"]:

            if word.lower() in lower:
                return True

        return False

    # ---------------------------------------------------------

    @staticmethod
    def contains_link(text: str):

        pattern = r"(http[s]?://|www\.|discord\.gg|youtu\.be|youtube\.com)"

        return re.search(pattern, text, re.IGNORECASE) is not None

    # ---------------------------------------------------------

    def replace_words(self, text: str):

        for old, new in self.replace.items():

            text = text.replace(old, new)

        return text

    # ---------------------------------------------------------

    @staticmethod
    def remove_symbols(text: str):

        return re.sub(
            r"[^\w\sА-Яа-яЁёІіЇїЄє]",
            "",
            text
        )

    # ---------------------------------------------------------

    @staticmethod
    def remove_emojis(text: str):

        emoji = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002700-\U000027BF"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )

        return emoji.sub("", text)

    # ---------------------------------------------------------

    @staticmethod
    def limit_letters(text: str):

        return re.sub(
            r"(.)\1{3,}",
            r"\1\1\1",
            text
        )