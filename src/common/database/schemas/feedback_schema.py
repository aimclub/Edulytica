from pydantic import BaseModel, EmailStr


class FeedbackIn(BaseModel):
    name: str
    email: EmailStr
    text: str
