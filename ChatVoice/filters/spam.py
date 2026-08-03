import time


class SpamFilter:

    def __init__(self, config: dict):

        self.config = config["filters"]

        self.last_messages = {}

    # ---------------------------------------------------------

    def check(self, username: str, message: str) -> bool:
        """
        True  -> сообщение можно обработать
        False -> сообщение считается спамом
        """

        if not self.config["ignore_duplicate_messages"]:
            return True

        timeout = self.config["duplicate_timeout"]

        current_time = time.time()

        key = (username.lower(), message.strip().lower())

        if key in self.last_messages:

            last_time = self.last_messages[key]

            if current_time - last_time < timeout:
                return False

        self.last_messages[key] = current_time

        self.cleanup(current_time)

        return True

    # ---------------------------------------------------------

    def cleanup(self, current_time: float):

        timeout = self.config["duplicate_timeout"]

        expired = []

        for key, timestamp in self.last_messages.items():

            if current_time - timestamp > timeout:
                expired.append(key)

        for key in expired:
            del self.last_messages[key]

    # ---------------------------------------------------------

    def clear(self):

        self.last_messages.clear()

    # ---------------------------------------------------------

    def count(self):

        return len(self.last_messages)