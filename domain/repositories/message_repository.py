from sqlalchemy.orm import Session

from api.models import MessageModel


class MessageRepository:
    def __init__(self, session:Session):
        self.session = session

    def get_messages(self, workspace_id: str):
        return self.session.query(MessageModel).filter_by(workspace_id=workspace_id).order_by(MessageModel.created_at.asc()).all()

    def create_message(self, workspace_id:str, role:MessageModel, message:str):
        message = MessageModel(workspace_id, role, message)
        self.session.add(message)
        self.session.commit()


