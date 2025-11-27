from domain.entities.workspace import Workspace
from domain.repositories.workspace_db import Workspace_DB
from uuid import UUID
w = Workspace("first ws", 1)
db = Workspace_DB()
db.save(w)
r = db.retrieve(UUID("56fd7680-f5f4-4b9e-a7c5-7b655ded1b33"))
print(r)
