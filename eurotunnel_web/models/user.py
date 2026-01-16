from pydantic import BaseModel, Field, NonNegativeInt


class User(BaseModel):
    id: NonNegativeInt
    name: str = Field(..., min_length=2)
