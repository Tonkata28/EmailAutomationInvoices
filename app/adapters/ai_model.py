from abc import ABC, abstractmethod
import base64
from pathlib import Path
from fastapi import UploadFile
from google import genai
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

from config import GEMINI_API_KEY

type InvoiceProvider = Literal["VIVACOM", "ViK"]

class InvoiceMetaData(BaseModel):
    is_invoice: bool
    provider: InvoiceProvider|None = None
    id: str
    date_of_issue: datetime


class BaseGenerativeModel(ABC):
    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, value):
        if not value:
            raise Exception("API key is invalid!")

        self.__api_key = value

    @abstractmethod
    def extract(self, file: UploadFile) -> InvoiceMetaData:
        pass


class GeminiGenerativeModel(BaseGenerativeModel):

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def extract(self, email_body: str, file_path: Path) -> InvoiceMetaData:
        # gets the document and determines if it is an invoice and extracts the fields in InvoiceMetaData

        uploaded_file = self.client.files.upload(file=file_path)
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                f"Extract the wanted properties in the format specified: {email_body}",
                uploaded_file
            ],
            config={
                'response_mime_type': 'application/json',
                'response_schema': InvoiceMetaData,
            }
        )

        print(response.text)
        assert response.text is not None
        return InvoiceMetaData.model_validate_json(response.text)


class CustomGenerativeModel(BaseGenerativeModel):
    pass


assert GEMINI_API_KEY is not None
model = GeminiGenerativeModel(api_key=GEMINI_API_KEY)