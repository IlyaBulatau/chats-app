from abc import ABC

from pydantic import BaseModel, ConfigDict


class BaseForm(ABC, BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, frozen=True)
