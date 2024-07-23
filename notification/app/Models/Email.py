from pydantic import BaseModel

class EmailRequest(BaseModel):
    to: list[str]
    subject: str
    body: str