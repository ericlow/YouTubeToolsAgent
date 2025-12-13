from datetime import datetime

from api.models.message_model import MessageModel
from api.models.video_model import VideoModel
#from domain.entities.workspace import Workspace
#from domain.repositories.workspace_db import Workspace_DB
from uuid import UUID

from api.models import WorkspaceVideoModel, WorkspaceModel, UserModel
from infrastructure.orm_database import get_session

def headline(val:str):
    print(f'====== {val} ======')

s = next(get_session())
headline('Read all Users')

users = s.query(UserModel).order_by(UserModel.created_at.desc()).limit(3).all()
for u in users:
    print(u)

# create a new user
u = UserModel()
s.add(u)
s.commit()

headline('Read all Workspaces')
workspaces = s.query(WorkspaceModel).order_by(WorkspaceModel.created_at.desc()).limit(3).all()
for w in workspaces:
    print(w)

headline('Get last Workspace')
w = workspaces[0]
print(w)

# print messages
messages = s.query(MessageModel).filter_by(workspace_id=w.workspace_id).\
    order_by(MessageModel.created_at.asc()).all()
for m in messages:
    print (m)

# print videos
workspace_videos = s.query(WorkspaceVideoModel).filter_by(workspace_id=w.workspace_id).all()

# get video list
vids = []
for ws_v in workspace_videos:
    vids.append(ws_v.video_id)

videos = s.query(VideoModel).filter(VideoModel.video_id.in_(vids)).all()
for v in videos:
    print(v)

headline('Create new Workspace')
# get last created user
last_user = s.query(UserModel).order_by(UserModel.created_at.desc()).first()

# associate last user with new workspace
ws_name = datetime.now().strftime("%b %d %H:%M")
workspace = WorkspaceModel(last_user.user_id,ws_name)
# save workspace to DB
#print(workspace.workspace_id)
s.add(workspace)
s.commit()
print(workspace.workspace_id)

# add a message to the workspace
m1 = MessageModel(workspace.workspace_id, "user", "hey can you help me out?")
m2 = MessageModel(workspace.workspace_id, "assistant", "happy to assist")
m3 = MessageModel(workspace.workspace_id, "user", "can you analyze a video?")
s.add(m1)
s.add(m2)
s.add(m3)
s.commit()
print(m1)
print(m2)
print(m3)
# add a video to the workspace
v = VideoModel("http://www.youtube.com/vid1", "transcript 1", "title 1", "channel 1", "summary")
s.add(v)
s.commit()
print(v)

wvm = WorkspaceVideoModel(workspace.workspace_id, v.video_id)
s.add(wvm)
s.commit()
print(wvm)
