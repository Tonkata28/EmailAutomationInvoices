import base64
from email.message import EmailMessage, MIMEPart
from googleapiclient.errors import HttpError
from app.auth.gmail_service import gmail_service
from app.config import settings
from app.errors.error_codes import ErrorSpec
from app.models.clients import ClientConfig
from app.models.gmail_messages import Message, MessagePart
from app.services.handle_invoice_data import bytes_to_text

    
def load_history_id():

    data = gmail_service.users().getProfile(userId='me').execute()

    # try:
    #     # data.raise_for_status()

    # except Exception as e:

    #     # try authorizing gmail if the error is authorization error
    #     # possibly could be no network connection, so the error might be not being able to connect to the API

    return data.get("historyId")


def send_email(message_body: str, invoice_pdf: bytes, client: ClientConfig) -> None:
    try:
        message = EmailMessage()

        message.set_content(message_body)

        message["To"] = client.accountant_email
        message["From"] = client.gmail
        message["Subject"] = f"Фактури {client.firm_name}"
        message.add_attachment(invoice_pdf, maintype="application", subtype="pdf", filename="alianto-invoice")

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode() # POSSIBLE PROBLEM!

        create_message = {"message": {"raw": encoded_message}}
        # pylint: disable=E1101
        send_message = (
            gmail_service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )

        print(f'Email id: {send_message["id"]}\nEmail message: {send_message["message"]}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        email = None

    return email


def get_email_text(message: Message) -> str | ErrorSpec:
    try:
        # it's simply impossible even where there is no body for the email to not have this part at least existing
        base_part = next(p for p in message["payload"]["parts"] if p["partId"] == "0")["parts"]

        # emails with no body are considered suspicious, but in future upgrades might consider changing this
        email_body_part: MessagePart = next(
            p for p in base_part 
                if (
                    p["partId"] == "0.0" and
                    p["mimeType"] == "text/plain" and
                    any([
                        h["name"] == "Content-Transfer-Encoding" and h["value"] == "base64" for h in p["headers"]
                    ])))

        email_text_b64: str|None = email_body_part["body"].get("data")

        if email_text_b64 is None:
            raise Exception("No found body in email!")
        

    except StopIteration as e:
        print(f"Exception raised : {e} (possibly no email body found)")

    except KeyError as e:
        print(f"Exception raised: {e} (possibly wrong format detected)")

    except Exception:
        return ErrorSpec(
            code=200,
            message="Invalid e-mail format detected!"
        )

    return bytes_to_text(base64.urlsafe_b64decode(str(email_text_b64)))