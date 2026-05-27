from pydantic import BaseModel
from typing import List


class Source(BaseModel):
    content: str
    source: str


class QAResponse(BaseModel):
    answer: str
    sources: List[Source]