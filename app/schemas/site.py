from datetime import date

from infrastructure.models.site import CountryEnum
from pydantic import BaseModel, ConfigDict, Field


class GroupResponse(BaseModel):
    id: int
    name: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class SiteBase(BaseModel):
    name: str = Field(..., example="Solar Plant A")
    country: CountryEnum = Field(..., example="FR")
    installation_date: date = Field(..., example="2025-07-20")
    max_power_megawatt: float = Field(..., example=10.5)
    min_power_megawatt: float = Field(..., example=2.0)
    useful_energy_at_1_megawatt: float | None = Field(None, example=0.85)
    efficiency: float | None = Field(None, example=90.5)


class SiteCreate(SiteBase):
    group_ids: list[int] | None = []


class SiteUpdate(BaseModel):
    name: str | None = None
    country: CountryEnum | None = None
    installation_date: date | None = None
    max_power_megawatt: float | None = None
    min_power_megawatt: float | None = None
    useful_energy_at_1_megawatt: float | None = None
    efficiency: float | None = None
    group_ids: list[int] | None = []


class SiteResponse(SiteBase):
    id: int
    groups: list[GroupResponse] = []

    model_config = ConfigDict(from_attributes=True)
