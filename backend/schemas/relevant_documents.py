from pydantic import BaseModel, Field


class RelevantDocuments(BaseModel):

    relevant_indices: list[int] = Field(
         description=("Zero-based indices of document chunks "
                      "that directly support answering the question.")
    )