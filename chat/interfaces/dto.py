from abc import ABC
from pydantic import BaseModel, ConfigDict


class BaseDTO(ABC, BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, frozen=True)