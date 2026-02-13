from datetime import datetime, timedelta
from time import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from freezegun import freeze_time
from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    equal_to,
    has_entry,
    has_item,
    has_length,
    has_properties,
    instance_of,
)

from electricitybot import ElectricityChecker
from electricitybot.bot import PowerOutageInterval, UKRAINE_TZ
from electricitybot.settings import settings


@pytest.fixture
def tg_bot():
    tg_bot_mock = Mock(return_value=AsyncMock())
    with patch("telegram.Bot", tg_bot_mock):
        yield tg_bot_mock


@patch("electricitybot.bot.sleep", Mock())
class TestElectricitybot:
    @patch("electricitybot.ElectricityChecker.check_electricity", Mock(return_value=True))
    def test_init(self, tg_bot):
        e_checker = ElectricityChecker()

        assert_that(e_checker, instance_of(ElectricityChecker))
        assert_that(
            e_checker,
            has_properties(
                chat_id=settings.chat_id,
                ip_to_check=settings.ip_to_check,
                timeout=settings.timeout,
                last_state_change_time=None,
            ),
        )

        tg_bot.assert_called_once_with(token=settings.api_token)

    @pytest.mark.parametrize("e_state", [True, False])
    @patch("electricitybot.ElectricityChecker.check_electricity", Mock(return_value=True))
    def test_build_message(self, e_state):
        e_checker = ElectricityChecker()
        message = e_checker.build_message(e_state)

        assert_that(message, equal_to(ElectricityChecker.power_messages[e_state]))

    @freeze_time("2022-04-15")
    @pytest.mark.parametrize("e_state", [True, False])
    @patch("electricitybot.ElectricityChecker.check_electricity", Mock(return_value=True))
    def test_build_message_with_stat(self, e_state):
        e_checker = ElectricityChecker()
        e_checker.last_state_change_time = time() - 3719  # 1 hour, 1 minute and 59 seconds
        stat_message = {
            True: "(світла не було 1 год. 1 хв.)",
            False: "(світло було 1 год. 1 хв.)",
        }
        message = e_checker.build_message(e_state)

        assert_that(message, equal_to(f"{ElectricityChecker.power_messages[e_state]}\n{stat_message[e_state]}"))

    @patch("electricitybot.ElectricityChecker.check_electricity", Mock(return_value=True))
    def test_ping(self):
        with patch("subprocess.run", Mock(return_value=Mock(returncode=0))) as run_mock:
            e_checker = ElectricityChecker()
            e_checker.ip_to_check = "7.7.7.7"
            ping_result = e_checker.ping()

        assert_that(ping_result, equal_to(True))

        run_mock.assert_called_once_with(["ping", "-c", "1", e_checker.ip_to_check], capture_output=True)

    @pytest.mark.parametrize("ping_result", [True, False])
    def test_check_electricity(self, ping_result):
        with patch("electricitybot.ElectricityChecker.ping", Mock(return_value=True)):
            e_checker = ElectricityChecker()

        with patch(
            "electricitybot.ElectricityChecker.ping",
            Mock(side_effect=[False] * e_checker.retries_count + [ping_result]),
        ) as ping_mock:
            result = e_checker.check_electricity()

        assert_that(result, equal_to(ping_result))
        assert_that(ping_mock.call_count, equal_to(e_checker.retries_count + 1))

    @patch("electricitybot.ElectricityChecker.check_electricity", Mock(side_effect=[True, False]))
    def test_check_e_state_and_send(self, tg_bot):
        e_checker = ElectricityChecker()
        message_to_send = "test_message"
        with patch("electricitybot.ElectricityChecker.build_message", Mock(return_value=message_to_send)):
            e_checker.check_e_state_and_send()

        assert_that(e_checker.previous_e_state, equal_to(False))

        tg_bot().send_message.assert_called_once_with(
            chat_id=e_checker.chat_id, message_thread_id=e_checker.thread_id, text=message_to_send
        )

    @pytest.mark.parametrize("e_state", [True, False])
    def test_save_stat(self, e_state):
        e_checker = ElectricityChecker()
        date_to_mock = UKRAINE_TZ.localize(datetime.fromisoformat("2022-04-15 12:34:01"))

        intervals = []
        start_time = date_to_mock
        end_time = None

        if e_state:
            start_time = date_to_mock - timedelta(hours=3, minutes=4)
            end_time = date_to_mock
            intervals = [PowerOutageInterval(start_time=start_time)]

        db_mock = MagicMock(get=Mock(side_effect=lambda *args, **kwargs: intervals))

        with patch("electricitybot.ElectricityChecker.db", db_mock), freeze_time(date_to_mock):
            e_checker.save_stat(e_state)

        db_mock.__setitem__.assert_called_once()

        assert_that(
            db_mock.__setitem__.call_args.args,
            contains_exactly(
                "intervals",
                all_of(
                    has_length(1),
                    has_item(
                        has_properties(
                            start_time=start_time,
                            end_time=end_time,
                        )
                    ),
                ),
            ),
        )

    def test_save_stat_when_no_interval(self):
        e_checker = ElectricityChecker()
        date_to_mock = UKRAINE_TZ.localize(datetime.fromisoformat("2022-04-15 12:34:01"))

        db_mock = {}
        with patch("electricitybot.ElectricityChecker.db", db_mock), freeze_time(date_to_mock):
            e_checker.save_stat(True)

        assert_that(db_mock, has_entry("intervals", has_length(0)))
