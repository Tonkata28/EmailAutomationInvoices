from datetime import datetime
import base64
import io
from app.auth.gmail_service import gmail_service
from app.data.data import SenderManager
from app.models.gmail_messages import Message, MessagePart
import re


def convert_to_pdf(message: Message):
    bytes_part: MessagePart|None = next((p for p in message["payload"]["parts"] if p["mimeType"] == "application/pdf"), None)
    
    if bytes_part is None:
        # go to scraping only if the sender is EVN, otherwise send troubleshoot notification to Telegram or whatever
        return

    data_bytes: str|None = bytes_part["body"].get("data")

    if data_bytes is None and bytes_part["body"]["attachmentId"] is not None:
        response = gmail_service.users().messages().attachments().get(
                        userId='me',
                        messageId=message["id"],
                        id=bytes_part["body"]["attachmentId"]
                    ).execute()
        data_bytes = response["data"]

    elif data_bytes is None and bytes_part["body"]["attachmentId"] is None:
        # Ignore email, since pdf file is basically empty somehow
        
        return

    assert data_bytes is not None
    return base64.urlsafe_b64decode(data_bytes)


def bytes_to_text(content: bytes) -> str:
    import pdfplumber
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() or ""

    return full_text


def extract_invoice_data(pdf_bytes: bytes):
    """
        Extracts the needed data from the invoice
    """
    # 1. Convert the pdf bytes into text, so we can extract the data with regex (InvoiceRecord)

    full_text = bytes_to_text(pdf_bytes)

    match_object = re.search("ФАКТУРА №: ([0-9]+)", full_text, flags=re.U)

    if match_object is None:
        raise Exception()

    invoice_id = match_object.group(1)

    match_object = re.search("Дата на данъчно събитие: ([0-9]{2}.[0-9]{2}.[0-9]{4})", full_text, flags=re.U)

    if match_object is None:
        raise Exception()

    timestamp = datetime.strptime(match_object.group(1), '%d.%m.%Y')


    match_object = re.search("Обща стойност на услугите ([0-9]+.[0-9]+) €", full_text, flags=re.U)

    if match_object is None:
        raise Exception()

    price = float(match_object.group(1))

    return invoice_id, timestamp, price


def format_email_body(timestamp: datetime, sender_name: str) -> str:    
    days_in_bulgarian = {1: 'януари', 2: 'февруари', 3: 'март', 4: 'април', 5: 'май', 6: 'юни', 7: 'юли', 8: 'август', 9: 'септември', 10: 'октомври', 11: 'ноември', 12: 'декември'}

    return f"Здрасти,\n\tТова са фактурите от {sender_name} за месец {days_in_bulgarian[int(datetime.strftime(timestamp, '%m'))]}"