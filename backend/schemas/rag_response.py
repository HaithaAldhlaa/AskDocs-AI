from pydantic import BaseModel
from typing import List


class Source(BaseModel):
    filename: str
    path: str
    content: str


class RAGResponse(BaseModel):
    answer: str
    sources: List[Source]