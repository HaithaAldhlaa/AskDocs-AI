from pydantic import BaseModel


class ChatResponse(BaseModel):

    answer: str

    language: str

    needs_clarification: bool