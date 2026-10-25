"""Pydantic model used to validate individual air-quality records."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AirQualityRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    city: str = Field(min_length=1)
    country: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: datetime
    pm10: Optional[float] = Field(default=None, ge=0)
    pm2_5: Optional[float] = Field(default=None, ge=0)
    carbon_monoxide: Optional[float] = Field(default=None, ge=0)
    nitrogen_dioxide: Optional[float] = Field(default=None, ge=0)
    sulphur_dioxide: Optional[float] = Field(default=None, ge=0)
    ozone: Optional[float] = Field(default=None, ge=0)
    us_aqi: Optional[float] = Field(default=None, ge=0)
    european_aqi: Optional[float] = Field(default=None, ge=0)

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
