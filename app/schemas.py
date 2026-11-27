"""Kiểm cấu hình và payload HTTP; dùng giờ Hà Nội khi kiểm ngày quá khứ."""
import datetime as dt
import unicodedata
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, field_validator, model_validator


def today_hanoi():
    return dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()


def clean_nickname(value):
    value = " ".join(unicodedata.normalize("NFC", value).split())
    if not value or any(unicodedata.category(c).startswith("C") for c in value):
        raise ValueError("Biệt danh không được trống hoặc chứa ký tự điều khiển.")
    return value


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class JoinGroup(Payload):
    nickname: str = Field(min_length=1, max_length=40)

    @field_validator("nickname")
    @classmethod
    def nickname_valid(cls, value):
        return clean_nickname(value)


class CreateGroup(JoinGroup):
    city_id: Literal["ha_noi"] = "ha_noi"
    scope: Literal["noi_thanh"] = "noi_thanh"
    date: dt.date
    start_time: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    start_id: str = Field(min_length=1, max_length=100)
    budget_total: StrictInt = Field(ge=0, le=1_000_000_000)
    mode: Literal["xe_may", "o_to", "di_bo"]

    @field_validator("date")
    @classmethod
    def not_in_past(cls, value):
        if value < today_hanoi():
            raise ValueError("Ngày đi không được ở trong quá khứ theo giờ Hà Nội.")
        return value

    @model_validator(mode="after")
    def ordered_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("Giờ kết thúc phải sau giờ bắt đầu trong cùng ngày.")
        return self


class DeckRequest(Payload):
    member_id: str = Field(min_length=1, max_length=64)


class SwipeRequest(DeckRequest):
    place_id: str = Field(min_length=1, max_length=100)
    liked: StrictBool


class UndoRequest(DeckRequest):
    place_id: str = Field(min_length=1, max_length=100)
