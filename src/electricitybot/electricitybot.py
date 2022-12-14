import subprocess
from time import sleep, time

import telegram

from .settings import settings


class ElectricityChecker:
    power_messages = {
        True: "🔋Є світло",
        False: "🪫Відключено електропостачання",
    }

    def __init__(self):
        self.chat_id = settings.chat_id
        self.ip_to_check = settings.ip_to_check
        self.retries_count = settings.retries_count
        self.timeout = settings.timeout
        self.thread_id = settings.thread_id
        self.tg_bot = telegram.Bot(token=settings.api_token)
        self.previous_e_state = self.check_electricity()
        self.last_state_change_time = None

    def ping(self):
        result = subprocess.run(["ping", "-c", "1", self.ip_to_check], capture_output=True)
        return result.returncode == 0

    def check_electricity(self):
        if not self.ping():
            for i in range(self.retries_count):
                sleep(2)
                if self.ping():
                    return True
            return False
        else:
            return True

    def build_message(self, current_e_state: bool):
        message = self.power_messages[current_e_state]
        if self.last_state_change_time:
            delay = time() - self.last_state_change_time
            delay_hours = int(delay // 3600)
            delay_minutes = int(delay % 3600) // 60
            stat = f"{delay_hours} год. {delay_minutes} хв."
            message += f"\n(світла не було {stat})" if current_e_state else f"\n(світло було {stat})"

        return message

    def check_and_send(self):
        current_e_state = self.check_electricity()
        if self.previous_e_state != current_e_state:
            message = self.build_message(current_e_state)
            self.tg_bot.send_message(chat_id=self.chat_id, message_thread_id=self.thread_id, text=message)
            self.previous_e_state = current_e_state
            self.last_state_change_time = time()

    def run(self):  # pragma: no cover
        while True:
            self.check_and_send()
            sleep(self.timeout)


def run_bot():  # pragma: no cover
    ElectricityChecker().run()
