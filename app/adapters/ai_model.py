from abc import ABC, abstractmethod
from fastapi import UploadFile
from google import genai
from pydantic import BaseModel
from google.genai import types

from app.config import settings

class ExtractionInfo(BaseModel):
    is_invoice: bool
    keywords: list[str] | None


class RegardsInvoiceInfo(BaseModel):
    is_invoice: bool


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
    def extract_keywords(self, file: UploadFile) -> ExtractionInfo:
        pass


class GeminiGenerativeModel(BaseGenerativeModel):

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def extract_keywords(self, email_body: str, recall=0) -> ExtractionInfo|None:

        if recall == 2:
            return None

        # gets the document and determines if it is an invoice and extracts the fields in InvoiceKeywords

        # uploaded_file = self.client.files.upload(file=file_path)
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                "Your task for now is to determine if this email body text regards an invoice." + 
                "If it is an invoice, weigh the probability of this to be a boilerplate email and provide keywords with which you would check this to be absolutely sure it's regarding an invoice." + 
                "If you do not think this is possible to be checked with keywords, leave the keywords as null: ",
                email_body
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionInfo,
                thinking_config=types.ThinkingConfig(thinking_budget=5000),
            )
        )

        if response.text is None:
            print("None returned as response from gemini")
            return self.extract_keywords(email_body, recall=recall + 1)

        return ExtractionInfo.model_validate_json(response.text)

    def determine_email(self, email_body: str) -> RegardsInvoiceInfo:

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                "Determine if this email body text regards an invoice.",
                email_body
            ],
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=RegardsInvoiceInfo,
                thinking_config=types.ThinkingConfig(thinking_budget=5000),
            )
        )

        if response.text is None:
            print("None returned as response from gemini")
            return RegardsInvoiceInfo(is_invoice=False)

        return RegardsInvoiceInfo.model_validate_json(response.text)


class CustomGenerativeModel(BaseGenerativeModel):
    pass

model = GeminiGenerativeModel(api_key=settings.gemini_api_key)