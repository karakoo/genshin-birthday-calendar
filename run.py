from datetime import date, datetime, timedelta
from itertools import chain
from pathlib import Path
from typing import Literal

from httpx import AsyncClient
from pydantic import BaseModel, PositiveInt

from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event, EventStatus
from ical.parsing.property import ParsedProperty
from ical.types import Frequency, Recur

LANGUAGE: Literal[
    "chs",
    "cht",
    "en",
    "fr",
    "de",
    "es",
    "pt",
    "ru",
    "jp",
    "kr",
    "th",
    "vi",
    "id",
    "tr",
    "it",
] = "chs"

client = AsyncClient()


class Birthday(BaseModel):
    month: PositiveInt
    day: PositiveInt


class Item(BaseModel):
    id: PositiveInt
    name: str
    birthday: Birthday


async def main():
    now = datetime.now()
    # noinspection SpellCheckingInspection
    calendar = Calendar(
        calscale="GREGORIAN",
        method="PUBLISH",
        prodid="-//Karako//Genshin Impact Birthday Calendar 0.1.0//CHS",
        version="2.0",
        extras=[
            ParsedProperty(name="name", value="原神生日日历", params=None),
            ParsedProperty(name="x-wr-calname", value="原神生日日历", params=None),
            ParsedProperty(name="timezone-id", value="Asia/Shanghai", params=None),
            ParsedProperty(name="x-wr-timezone", value="Asia/Shanghai", params=None),
            ParsedProperty(name="X-PUBLISHED-TTL", value="PT1H", params=None),
            ParsedProperty(name="x-wr-caldesc", value="提瓦特全角色生日日历", params=None),
            ParsedProperty(
                name="REFRESH-INTERVAL;VALUE=DURATION", value="PT1H", params=None
            ),
        ],
    )
    host = f"https://api.ambr.top/v2/{LANGUAGE}/avatar"
    response = await client.get(host)
    json_data = response.json()
    for data in [
        v for _, v in json_data["data"]["items"].items() if v["name"] != "旅行者"
    ]:
        for i in chain(*[list({j, 0 - j}) for j in range(4)]):
            try:
                begin = date(now.year + i, data["birthday"][0], data["birthday"][1])
                break
            except ValueError:
                continue
        # noinspection PyUnboundLocalVariable
        event = Event(
            summary=f"{data['name']}的生日",
            dtstart=begin,
            duration=timedelta(days=1),
            rrule=Recur(freq=Frequency.YEARLY),
            status=EventStatus.CONFIRMED,
            transp="TRANSPARENT",
        )
        calendar.events.append(event)

    await client.aclose()

    filename = Path("calendar.ics")
    with filename.open("w", encoding="utf-8") as ics_file:
        ics_file.write(IcsCalendarStream.calendar_to_ics(calendar))


def __main__():
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    __main__()
