from typing import Literal

from pydantic import BaseModel


class DocumentSelection(BaseModel):
    path: str


class SubmittalSelection(BaseModel):
    manufacturer: str
    roofing_system: Literal["TPO", "PVC", "EPDM"]
    documents: list[DocumentSelection]