import io
from collections import defaultdict
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

weekdays_map = {
    1: "пн.",
    2: "вт.",
    3: "ср.",
    4: "чт.",
    5: "пт.",
    6: "сб.",
    7: "нд.",
}


def build_chart(intervals: list) -> bytes:  # pragma: nocover
    def to_hours(dt):
        return dt.hour + dt.minute / 60 + dt.second / 3600

    days_data = defaultdict(list)

    for start, end in intervals:
        current_day = start.date()
        last_day = end.date()

        while current_day <= last_day:
            day_start = datetime.combine(current_day, datetime.min.time())
            day_end = day_start + timedelta(days=1)

            interval_start = max(start, day_start)
            interval_end = min(end, day_end)

            if interval_start < interval_end:
                start_h = to_hours(interval_start)
                duration_h = (interval_end - interval_start).total_seconds() / 3600
                days_data[current_day].append((start_h, duration_h))

            current_day += timedelta(days=1)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [3, 1]})
    fig.suptitle("Статистика світла (за адресою Ващенка 3) за тиждень", fontsize=16)
    fig.patch.set_facecolor("#f0f0f0")

    days = sorted(days_data.keys())

    ax1.set_facecolor("#fff3e0")
    ax1.grid(True, axis="y", linestyle="--", alpha=0.5)
    ax1.set_xlim(-0.2, len(days) - 0.2)
    ax1.set_ylim(0, 24)
    ax1.set_ylabel("Світло погодинно")
    ax1.set_xticks([i + 0.4 for i in range(len(days))])
    ax1.set_xticklabels([])
    ax1.set_yticks(range(0, 25, 2))
    ax1.set_yticklabels([f"{h:02d}:00" for h in range(0, 25, 2)])

    percentages = []
    occupied_hours_list = []

    for day in days:
        occupied = sum(duration for _, duration in days_data[day])
        occupied_hours_list.append(occupied)
        percentages.append((24 - occupied) / 24 * 100)

    x = [i + 0.4 for i in range(len(days))]

    ax2.set_facecolor("#fff3e0")
    ax2.grid(True, axis="y", linestyle=":", alpha=0.3)
    ax2.plot(x, percentages, marker="o")
    ax2.set_xlim(-0.2, len(days) - 0.2)
    ax2.set_ylim(-40, 160)
    ax2.set_xlabel("Дата")
    ax2.set_ylabel("Світло у %")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{day.day}.{day.month} ({weekdays_map[day.isoweekday()]})" for day in days])
    ax2.set_yticks(range(0, 101, 20))
    ax2.set_yticklabels([f"{v}%" for v in range(0, 101, 20)])

    for i, day in enumerate(days):
        ax1.broken_barh([(i, 0.8)], (0, 24), facecolors="green")

        for start_h, duration_h in days_data[day]:
            ax1.broken_barh([(i, 0.8)], (start_h, duration_h), facecolors="red")


    for i, (pct, occupied) in enumerate(zip(percentages, occupied_hours_list)):
        free = 24 - occupied

        occ_h = int(occupied)
        occ_m = int((occupied - occ_h) * 60)

        free_h = int(free)
        free_m = int((free - free_h) * 60)

        ax2.text(
            i + 0.4,
            pct + 10,
            f"{pct:.0f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )

        ax2.text(
            i + 0.4,
            -30,
            f"{occ_h}ч {occ_m}м",
            ha="center",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="orange", alpha=0.7),
        )

        ax2.text(
            i + 0.4,
            150,
            f"{free_h}ч {free_m}м",
            ha="center",
            va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7),
        )

    buffer = io.BytesIO()
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight", pad_inches=0.35)
    buffer.seek(0)

    return buffer.getvalue()
