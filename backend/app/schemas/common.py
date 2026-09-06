from pydantic import BaseModel, Field
class Message(BaseModel):
    message: str
class Pagination(BaseModel):
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
