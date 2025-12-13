from sqlalchemy.orm import Session

from api.models import VideoModel, WorkspaceVideoModel, UserModel


class UserRepository:
    def __init__(self, session: Session):
        self.session = session


    def save_summary(self, workspace_id:str, video_id:int, summary:str):
        workspace_videos = self.session.query(WorkspaceVideoModel).filter_by(workspace_id=workspace_id).all()
        # we should save the summary to this object

        video = self.session.query(VideoModel).filter_by(video_id=video_id).all()

        self.session.add(video)
        self.session.commit()

    def get_videos(self, workspace_id):
        workspace_videos = self.session.query(WorkspaceVideoModel).filter(WorkspaceVideoModel.workspace_id == workspace_id).all()

        result = []
        for record in workspace_videos:
            result.append({
                'url': record.video.url,
                'transcript': record.video.transcript[:100],
                'title': record.video.title,
                'author': record.video.channel,
                'summary': record.summary  # From junction table now
            })
        return result

    def create_user(self) -> dict:
        user = UserModel()
        self.session.add(user)
        self.session.commit()
        return {
            'user_id': user.user_id,
            'created_at': user.created_at.isoformat()
        }


    def get_user(self):
        pass

    def get_users(self):
        pass