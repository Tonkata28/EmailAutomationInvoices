# if db record of the state table doesn't exist, get the latest history id and start from there
from app.data.data import engine, EmailProgress
from sqlmodel import Session, select, update

class StateManager():

    @staticmethod
    def get_history_id() -> str:
        with Session(engine) as session:
            history_id = session.exec(select(EmailProgress).where(EmailProgress.key == "main_cursor")).one().history_id

        return history_id

    @staticmethod
    def set_history_id(history_id: str) -> None:
        with Session(engine) as session:
            cursor = session.exec(select(EmailProgress).where(EmailProgress.key == "main_cursor")).one()
            cursor.history_id = history_id

            session.add(cursor)
            session.commit()