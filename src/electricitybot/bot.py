import shelve
import subprocess
from datetime import date, datetime, timedelta
from time import sleep, time
from typing import Any

import pytz
import telegram
from asgiref.sync import async_to_sync

from electricitybot.chart import build_chart
from electricitybot.settings import settings

UKRAINE_TZ = pytz.timezone("Europe/Kyiv")  # <3


class PowerOutageInterval:
    def __init__(self, start_time: datetime, end_time: datetime | None = None):
        self._start_time = start_time
        self._end_time = end_time

    def __repr__(self):
        return f"{self.__class__.__name__} (start_time={self.start_time}, end_time={self.end_time})"

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def end_time(self) -> datetime:
        return self._end_time

    def finalize(self, end_time: datetime):
        self._end_time = end_time


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
        self.stats_last_send_date = None

    @property
    def db(self) -> shelve.Shelf[Any]:
        return shelve.open("power_outage_intervals")

    def ping(self) -> bool:
        result = subprocess.run(["ping", "-c", "1", self.ip_to_check], capture_output=True)
        return result.returncode == 0

    def check_electricity(self) -> bool:
        if not self.ping():
            for i in range(self.retries_count):
                sleep(2)
                if self.ping():
                    return True
            return False
        else:
            return True

    def build_message(self, current_e_state: bool) -> str:
        message = self.power_messages[current_e_state]
        if self.last_state_change_time:
            delay = time() - self.last_state_change_time
            delay_hours = int(delay // 3600)
            delay_minutes = int(delay % 3600) // 60
            stat = f"{delay_hours} год. {delay_minutes} хв."
            message += f"\n(світла не було {stat})" if current_e_state else f"\n(світло було {stat})"

        return message

    def save_stat(self, current_e_state: bool):
        intervals: list[PowerOutageInterval] = self.db.get("intervals", [])
        if not current_e_state:
            intervals.append(PowerOutageInterval(datetime.now(UKRAINE_TZ)))
        elif intervals:
            last_interval = intervals[-1]
            if not last_interval.end_time:
                last_interval.finalize(datetime.now(UKRAINE_TZ))

        self.db["intervals"] = intervals

    def check_and_send_stats(self):
        ukraine_now = datetime.now(UKRAINE_TZ)
        week_ago = UKRAINE_TZ.localize(datetime.combine(ukraine_now - timedelta(days=7), datetime.min.time()))
        day_start = UKRAINE_TZ.localize(datetime.combine(ukraine_now, datetime.min.time()))

        if not self.stats_last_send_date:
            self.stats_last_send_date: date = self.db.get(
                "stats_last_sent_date", (ukraine_now - timedelta(days=1)).date()
            )

        if (
            ukraine_now.date() != self.stats_last_send_date
            and ukraine_now.isoweekday() == settings.stats_day_of_week
            and ukraine_now.hour == settings.stats_hour
        ):
            self.db["stats_last_sent_date"] = ukraine_now.date()
            self.stats_last_send_date = ukraine_now.date()

            intervals: list[PowerOutageInterval] = self.db.get("intervals", [])
            filtered_intervals = []
            intervals_to_save = []
            for interval in intervals:
                # cut out intervals to work only with past week
                if interval.start_time.date() < week_ago.date():
                    if interval.end_time.date() < week_ago.date():
                        continue

                    new_interval = PowerOutageInterval(week_ago, interval.end_time)
                    interval = new_interval

                if interval.start_time.date() < ukraine_now.date():
                    if interval.end_time.date() >= ukraine_now.date():
                        new_interval = PowerOutageInterval(day_start, interval.end_time)
                        intervals_to_save.append(new_interval)

                        interval.finalize(day_start)

                    filtered_intervals.append((interval.start_time, interval.end_time))
                else:
                    intervals_to_save.append(interval)

            self.db["intervals"] = intervals_to_save

            if filtered_intervals:
                stats_image = build_chart(filtered_intervals)
                async_to_sync(self.tg_bot.send_photo)(
                    chat_id=self.chat_id,
                    message_thread_id=self.thread_id,
                    disable_notification=True,
                    caption="📊Статистика світла за тиждень",
                    photo=stats_image,
                )

    def check_e_state_and_send(self):
        if settings.send_weekly_stats:
            self.check_and_send_stats()

        current_e_state = self.check_electricity()

        if self.previous_e_state != current_e_state:
            if settings.send_weekly_stats:
                self.save_stat(current_e_state)

            message = self.build_message(current_e_state)
            async_to_sync(self.tg_bot.send_message)(
                chat_id=self.chat_id, message_thread_id=self.thread_id, text=message
            )
            self.previous_e_state = current_e_state
            self.last_state_change_time = time()

    def run(self):  # pragma: no cover
        while True:
            self.check_e_state_and_send()
            sleep(self.timeout)


def run_bot():  # pragma: no cover
    ElectricityChecker().run()


if __name__ == "__main__":  # pragma: nocover
    run_bot()
