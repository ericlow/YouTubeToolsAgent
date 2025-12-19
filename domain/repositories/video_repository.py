from typing import Protocol
from sqlalchemy.orm import Session
from api.models import VideoModel, WorkspaceVideoModel

class GetVideoArgs(Protocol):
    def execute(self, session: Session) -> dict | None: ...

class GetVideoArgsUrl(GetVideoArgs):
    def __init__(self, url: str):
        target_url = url.partition('&')[0]
        self.url = target_url

    def execute(self, session: Session) -> dict | None:
        video = session.query(VideoModel).filter_by(url=self.url).first()
        if video is None: return None
        return video.to_dict()

class GetVideoArgsWorkspaceVideoId(GetVideoArgs):
    def __init__(self, workspace_id:str, video_id:int) -> VideoModel:
        self.workspace_id = workspace_id
        self.video_id = video_id

    def execute(self, session: Session) -> dict | None:
        print(f"{self.workspace_id} / {self.video_id}")
        workspace_video = session.query(WorkspaceVideoModel).filter_by(workspace_id=self.workspace_id, video_id=self.video_id).first()
        return workspace_video.to_dict()


class VideoRepository:
    def __init__(self, session: Session):
        self.session = session
    def test(self, arg: GetVideoArgs):
        pass

    def save_video(self, workspace_id:str, video:dict) -> int:

        # get video
        videomodel = self.session.query(VideoModel).filter_by(url=video["url"]).first()
        # if video does not exist, create it
        if not videomodel:
            videomodel = VideoModel(url=video["url"], transcript=video["transcript"], title=video["title"], channel=video["author"])
            self.session.add(videomodel)
            self.session.flush()

        # get workspace_video
        workspace_video = self.session.query(WorkspaceVideoModel).filter_by(workspace_id=workspace_id, video_id=videomodel.video_id).first()
        # if does not exist, create it
        if not workspace_video:
            wvm = WorkspaceVideoModel(workspace_id=workspace_id, video_id=videomodel.video_id)
            self.session.add(wvm)
        self.session.commit()

        return videomodel.video_id

    def save_summary(self, workspace_id:str, video_id:int, summary:str):
        workspace_video = self.session.query(WorkspaceVideoModel).filter_by(workspace_id=workspace_id, video_id=video_id).first()
        workspace_video.summary = summary

        # add is not needed since this is an existing record
        self.session.commit()

    def get_videos(self, workspace_id):
        workspace_videos = self.session.query(WorkspaceVideoModel).filter(WorkspaceVideoModel.workspace_id == workspace_id).all()

        result = []
        for record in workspace_videos:
            result.append(record.to_dict())
        return result

    def get_video(self, arg: GetVideoArgs) -> dict:
        return arg.execute(self.session)

