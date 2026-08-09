from fastapi import APIRouter, UploadFile
from ..adapters.ai_model import model
from ..config import PROJECT_ROOT
from ..data.senders import senders

router = APIRouter()

# figure out best HTTP method, but POST for now and figure out why post is best, probably because it changes something

from pydantic import BaseModel, EmailStr


class EmailInfo(BaseModel):
    sender_email: EmailStr
    theme: str
    text: str
    invoice_file: UploadFile | None = None # should be a pdf/csv


# GitHub Actions is scanning for incoming emails from these senders
# When it finds an email, it returns:
## 


@router.post("/invoice/platform")
def scrape_email_info(
    email_info: EmailInfo
):
    # get the email content
    # determine if we need to login to platform based on this info (based on if we know a file is expected and there is one, otherwise fallback to logging in platform)
    # actually login in the platform
    # download documents
    # send all downloaded documents to wanted email
    # mark email as done

    # simulates actual checking
    if (email_info.invoice_file):
        # download file
        return

    pass


@router.post("/invoice/email")
def categorize_email(
    content
):
    print(content)
    # assume until here that the email is from vik/vivacom

    # filter if email is regarding an invoice based on keywords
    # if any([k not in email_info.text for k in senders[email_info.sender_email]["keywords"]]) or email_info.invoice_file is None:
    #     return {
    #         "code": 400, # or whatever is good for this,
    #         "message": "Email is not an invoice"
    #     }

    

    # invoice = model.extract(email_info.text, PROJECT_ROOT / "files" / "18331605835_20260722_0119735899.pdf")

    # save email and invoice to some storage

    # send invoice to accountant
    
    return {
        "code": 400,
        "message": "Succesfully received notification"
    }


