# from app.models.invoice import InvoiceRecord


db = {
    "last_history_id": None,
    "senders": {
        "noreply@vivacom.bg": {
            "keywords": ["е-Фактура", "файл", "налична"],
            "sender_name": "vivacom"
        }
    }
}

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session, select
from sqlalchemy.engine import URL


class InvoiceRecord(SQLModel, table=True):
    invoice_id: str = Field(primary_key=True) 
    invoice_file: bytes
    timestamp: datetime
    price: float
    sender_id: int
    email_id: str


class EmailProgress(SQLModel, table=True):
    key: str = Field(primary_key=True)
    history_id: str
    updated_at: datetime


# class InvoiceRe TODO


url_object = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="postgres",  # plain (unescaped) text
    host="localhost",
    database="invoices",
    port=5432
)


engine = create_engine(url_object, echo=True)

def create_invoice_record(
    id: str,
    sender_id: int,
    email_id: str,
    invoice_file: bytes,
    timestamp: datetime,
    price: float
) -> None:
    r = InvoiceRecord(invoice_id=id, sender_id=sender_id, email_id=email_id, invoice_file=invoice_file, timestamp=timestamp, price=price)

    with Session(engine) as session:
        session.add(r)

        session.commit()


class SenderKeyword(SQLModel, table=True):
    id: int|None = Field(primary_key=True, default=None)
    word: str
    

class SenderKeywordLink(SQLModel, table=True):
    keyword_id: int | None = Field(foreign_key="senderkeyword.id", primary_key=True)
    sender_id: int | None = Field(foreign_key="sender.id", primary_key=True)


# senders are added via the script dynamically, first time analyzed by AI, and all the AI does it makes a new record with new keywords in the database, no new code
# there is a gate for known and unknown senders and there could be an option of notifying in telegram if you want to add the new sender or not, otherwise it's automatically added


class Sender(SQLModel, table=True):
    id: int|None = Field(primary_key=True, default=None)
    email: str
    keywords: list["SenderKeyword"]|None = Relationship(link_model=SenderKeywordLink)
    name: str


class SenderManager():

    @staticmethod
    def determine_sender(
        sender_email: str      
    ) -> Sender:
        with Session(engine) as session:
            sender = session.exec(select(Sender).where(Sender.email == sender_email)).one()

        return sender

    @staticmethod
    def get_sender_name(
        id: int
    ) -> str:
        with Session(engine) as session:
            name = session.exec(select(Sender).where(Sender.id == id)).one().name

        return name


    @staticmethod
    def create_sender(
        email: str,
        name: str,
        keywords: list[str]|None = None
    ) -> Sender:
        with Session(engine) as session:

            if keywords is None:
                sender = Sender(email=email, name=name)
                session.add(sender)

            else:

                # add keywords for SenderKeyword db if the keywords do not exist
                sender_keywords: list[SenderKeyword] = []

                for w in keywords:
                    results = session.exec(select(SenderKeyword).where(SenderKeyword.word == w))
                    print(results.all())
                    if len(results.all()) == 0:
                        new_keyword = SenderKeyword(word=w)

                        session.add(new_keyword)
                        sender_keywords.append(new_keyword)

                    else:
                        sender_keywords.append(results.one())

                # map keywords to senders in the link table
                sender = Sender(email=email, name=name, keywords=sender_keywords)
                session.add(sender)

            session.commit()

            print(f"Sender after commit: {sender}")
            
            return sender

    @staticmethod
    def get_sender_keywords(sender_id: int) -> list[str]|None:
        
        with Session(engine) as session:
            kw = session.exec(select(Sender).where(Sender.id == sender_id)).one().keywords

            if kw is None:
                return None
            
            keywords = [s.word for s in kw]

        return keywords


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()
    SenderManager.create_sender("tonisimeonov33@gmail.com", "Antonio", ["Фактура"])
    with Session(engine) as session:
        session.add(EmailProgress(key="main_cursor", history_id="16554", updated_at=datetime.now()))

    session.commit()