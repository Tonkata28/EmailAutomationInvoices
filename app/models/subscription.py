from pydantic import BaseModel
from datetime import datetime


class SubscriptionMessage(BaseModel):
    data: str
    message_id: str
    publish_time: datetime


class SubscriptionRequest(BaseModel):
    message: SubscriptionMessage
