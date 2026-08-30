from fastapi import APIRouter


router = APIRouter(prefix="/api")

@router.get("/info")
def get_info():
    return {
        "name": "Email Invoice Automation",
        "spec": "This is an automation regarding extracting invoices from emails and forwarding them to a specified accountant email."
    }