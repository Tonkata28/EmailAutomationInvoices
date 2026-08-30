from dataclasses import dataclass

@dataclass
class ErrorSpec():
    code: int
    message: str