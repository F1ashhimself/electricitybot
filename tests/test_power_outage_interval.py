from datetime import datetime, timedelta

from freezegun import freeze_time
from hamcrest import assert_that, equal_to, has_properties

from electricitybot.bot import PowerOutageInterval


class TestPowerOutageInterval:

    @freeze_time("2022-04-15")
    def test_init(self):
        interval = PowerOutageInterval(datetime.now())

        assert_that(interval, has_properties(start_time=datetime.now(), end_time=None))

    @freeze_time("2022-04-15")
    def test_finalize(self):
        end_time = datetime.now() + timedelta(days=1)
        interval = PowerOutageInterval(datetime.now())
        interval.finalize(end_time)

        assert_that(interval.end_time, equal_to(end_time))

    @freeze_time("2022-04-15")
    def test_repr(self):
        start_time = datetime.now()
        end_time = datetime.now() + timedelta(days=1)
        interval = PowerOutageInterval(start_time, end_time)
        assert_that(
            repr(interval), equal_to(f"{PowerOutageInterval.__name__} (start_time={start_time}, end_time={end_time})")
        )
