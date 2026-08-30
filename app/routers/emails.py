from pathlib import Path
import re
from app.errors.error_codes import ErrorSpec
from app.models.clients import get_client
from app.models.gmail_messages import Message, MessagePart, UpdatesResponse
from app.models.subscription import SubscriptionRequest
from app.services.gmail import get_email_text, send_email
from app.services.handle_invoice_data import bytes_to_text, convert_to_pdf, extract_invoice_data, format_email_body
import json
from app.auth.gmail_service import gmail_service
from fastapi import APIRouter, status, Response
import base64
from app.data.data import SenderManager, create_invoice_record, db
from app.services.state import StateManager
from app.adapters.ai_model import model

router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])

@router.post(
        "/email", 
        status_code=status.HTTP_201_CREATED
    )
def categorize_email(
    request: SubscriptionRequest,
    response: Response
):

    # check history id of current update and save it for the next time
    data = json.loads(base64.b64decode(request.message.data))
    history_id = data["historyId"]

    # if settings.debug:
    #     p = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / f"notification-{history_id}"

    #     with open(p, 'w') as f:
    #         json.load(request, f, indent=2)

    # runs an HTTP request to the gmail API with the lastly updated historyId to see the new message updates
    updates: UpdatesResponse = gmail_service.users().history().list(userId='me', startHistoryId=StateManager.get_history_id(), labelId="Label_2314963774244779182", historyTypes=["messageAdded"]).execute()

    if updates.get('history') is None:
        print("Nothing is updated")
        return

    messages_added = next((u["messagesAdded"] for u in updates["history"] if u.get("messagesAdded") is not None), None)

    if messages_added is None:
        print("No actual message was added in update")
        return

    if len(messages_added) == 1:
        # case when notification is received on the moment and no messages are cached
        msg_id = messages_added[0]["message"]["id"]
        message_added: Message = gmail_service.users().messages().get(userId='me', id=msg_id).execute()

        # Keep in mind there must be a sender since, well, this is an email, it's impossible to not have this header in the payload
        sender = next(header["value"] for header in message_added["payload"]["headers"] if header['name'] == "From")
        search_object = re.search(r"(\w+) <([^@\s]+@[^@\s]+\.[^@\s]+)>", sender, flags=re.U)

        if search_object is None:
            return {
                "code": 200, # so there is no resend
                "message": "Invalid sender name"
            }

        email_text = get_email_text(message_added)

        if isinstance(email_text, ErrorSpec):
            return {
                "code": email_text.code,
                "message": email_text.message
            }

        sender_email: str = search_object.group(2)
        sender = SenderManager.determine_sender(sender_email)

        if sender is None:
            model_response = model.extract_keywords(email_text)

            if model_response is None or not model_response.is_invoice:
                return # just return and do not go on with the rest of the process

            sender_name: str = search_object.group(1)

            if not model_response.keywords:
                sender = SenderManager.create_sender(sender_email, sender_name)

            else:
                sender = SenderManager.create_sender(sender_email, sender_name, model_response.keywords)
        else:

            # Determine if message is actually regarding an invoice by knowing the sender's determined keywords if he has ones
            keywords = sender.keywords

            if keywords is None:
                is_regarding_invoice = model.determine_email(email_text)

                if not is_regarding_invoice:
                    return # message doesn't regard invoice, therefore no further processing

            else:

                for k in keywords:
                    if k.word not in email_text:
                        # Possible issues, but very unlikely -> 

                        # # somehow has gone through the gmail filter and is from this sender, but doesn't pass the sender default document
                        # # meaning one of these option:
                        # # -> 1. Sender does not use a boilerplate and in this case we have to call an LLM every time to validate it
                        # # -> 2. The keywords picked by the LLM are not correct

                        # # Case 1 should not happen, since we already test if the email is formed from a boilerplate
                        # # Case 2:
                        model_response = model.extract_keywords(email_text)

                        if model_response is None:
                            return

                        if not model_response.is_invoice:
                            return {
                                "message": "Body doesn't regard an invoice!"
                            }


        file_pdf = convert_to_pdf(message_added)
        if not file_pdf: # make exception for scraping here or earlier
            return {
                "message": "No pdf document attached to file" # although this shouldn't happen, since this is the type of filter we have, but it could be an attached image
            }

        invoice_id, timestamp, price = extract_invoice_data(file_pdf)
        print("Information extracted succesfully")

        email_body = format_email_body(timestamp, sender.name)
        # for now as draft only!
        # fake client_id for now
        if send_email(email_body, file_pdf, client=get_client(-1)) is None:
            response.status_code = 200 # auth scopes or some method might have changed
            return response

        create_invoice_record(
            id=invoice_id,
            sender_id=sender.id, # otherwise get id with sender via email # type: ignore -> for now
            email_id=message_added["id"],
            invoice_file=file_pdf,
            timestamp=timestamp,
            price=price
        )
        print("Invoice recorded succesfully")

    elif len(messages_added) > 1:
        pass
        # TODO

    # recording here, since the email is sent, invoice is recorded and no more actions are required
    db["last_history_id"] = history_id

    return {
        "message": "Succesfully received notification"
    }
