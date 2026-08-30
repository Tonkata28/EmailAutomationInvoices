from pydantic import BaseModel, EmailStr
from app.config import settings

class ClientConfig(BaseModel):
    gmail: EmailStr
    pass_evn: str
    firm_name: str
    accountant_email: EmailStr


# for now simulates getting a real client, must be a database query if more clients are introduced
def get_client(id: int):

    return ClientConfig(
        gmail=settings.gmail,
        pass_evn=settings.pass_evn,
        firm_name=settings.firm_name,
        accountant_email=settings.accountant_email
    )