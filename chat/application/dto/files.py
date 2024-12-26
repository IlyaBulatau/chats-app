from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FileReadDTO:
    name: str
    url: str
    type: str
