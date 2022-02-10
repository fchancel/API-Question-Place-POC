from pydantic import BaseModel, EmailStr
from pydantic.typing import List


class EmailValidation(BaseModel):
    email_body: str
    to_email: List[EmailStr]
    email_subject: str
