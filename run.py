from datetime import date, datetime, timedelta
from itertools import chain
from pathlib import Path
from typing import Any, Literal

from httpx import AsyncClient
from pydantic import BaseModel, PositiveInt

from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event, EventStatus
from ical.parsing.property import ParsedProperty
from ical.types import Frequency, Recur, Uri

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


# noinspection PyBroadException
async def request(url: str) -> dict[str, Any] | None:
    import asyncio

    for _ in range(10):
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return
            return response.json()
        except:
            await asyncio.sleep(1)


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
    if (
        json_data := await request(f"https://gi.yatta.moe/api/v2/{LANGUAGE}/avatar")
    ) is None:
        return
    for data in [
        v
        for _, v in json_data["data"]["items"].items()
        if v["name"] != "旅行者" and not v.get("beta", False)
    ]:
        new_json_data = await request(
            f"https://gi.yatta.moe/api/v2/{LANGUAGE}/avatarFetter/{data['id']}"
        )
        for i in [0 - j for j in range(1, 5)]:
            try:
                begin = date(now.year + i, data["birthday"][0], data["birthday"][1])
                break
            except ValueError:
                continue
        name = data["name"]
        # noinspection PyUnboundLocalVariable
        event = Event(
            summary=f"{name}的生日",
            dtstart=begin,
            duration=timedelta(days=1),
            rrule=Recur(freq=Frequency.YEARLY),
            status=EventStatus.CONFIRMED,
            transp="TRANSPARENT",
            url=Uri(f"https://wiki.biligame.com/ys/{data['name']}"),
            description=new_json_data["data"]["story"]["0"]["text"].replace("\\n", "\n")
            if new_json_data is not None
            else None,
        )
        calendar.events.append(event)
        print(name, "is OK")

    await client.aclose()

    filename = Path("calendar.ics")
    with filename.open("w", encoding="utf-8") as ics_file:
        ics_file.write(IcsCalendarStream.calendar_to_ics(calendar))


def __main__():
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    __main__()
