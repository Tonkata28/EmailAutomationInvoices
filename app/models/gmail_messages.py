from typing import Optional, TypedDict


class MessagePartBody(TypedDict):
    attachmentId: Optional[str]
    data: Optional[str]
    size: int


# class MessageSubPart(TypedDict):
#     partId: str
#     mimeType: str
#     fileName: str
#     body: MessagePartBody
#     parts: list["MessagePart"]




class Header(TypedDict):
    name: str
    value: str


class MessagePart(TypedDict):
    partId: str
    headers: list[Header]
    mimeType: str
    fileName: str
    body: MessagePartBody
    parts: list["MessagePart"]


class Payload(TypedDict):
    body: MessagePartBody
    parts: list[MessagePart]
    headers: list[Header]


class Message(TypedDict):
    id: str
    threadId: str
    labelIds: list[str]
    snippet: str
    historyId: str
    payload: Payload


class MessageAdded(TypedDict):
    message: Message


class History(TypedDict):
    id: str
    messages: list[Message]
    messagesAdded: list[MessageAdded]


class UpdatesResponse(TypedDict):
    history: list[History]
