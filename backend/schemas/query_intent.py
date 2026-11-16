from pydantic import BaseModel
from typing import Literal


class QueryIntent(BaseModel):

    intent: Literal[
        "knowledge_base",
        "general"
    ]

    reason: str