from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class FrontendConfigBase(BaseModel):
    config_key: str
    config_value: dict[str, Any]
    description: str | None = None


class FrontendConfigCreate(FrontendConfigBase):
    pass


class FrontendConfigUpdate(BaseModel):
    config_value: dict[str, Any] | None = None
    description: str | None = None


class FrontendConfigRead(FrontendConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
