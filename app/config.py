from dotenv import load_dotenv
import os

from pathlib import Path

load_dotenv(".env")

platforms_gmail = os.getenv("gmail")
passwordEVN = os.getenv("passwordEVN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if passwordEVN is None or platforms_gmail is None or GEMINI_API_KEY is None:
    raise Exception("Credentials not set! Program terminated!")
