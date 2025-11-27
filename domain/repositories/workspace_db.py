from domain.entities.workspace import Workspace
from infrastructure import database
from uuid import UUID

class Workspace_DB:
    def save(self, workspace: Workspace) -> None:
        db = database.get_connection()
        cursor = db.cursor()
        try:
            cursor.execute("""
            INSERT INTO workspaces (workspace_id, user_id, name, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (workspace_id) DO UPDATE
            SET name = EXCLUDED.name
            """, (
                str(workspace.workspace_id),
                workspace.user_id,
                workspace.name,
                workspace.created_at
            ))

            # update relationships between workspaces and videos
            for video_id in workspace.video_ids:
                cursor.execute(
                    """
                    INSERT INTO workspace_videos (workspace_id, video_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """, (str(workspace.workspace_id), video_id)
                )
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def retrieve(self, workspace_id: UUID) -> Workspace:
        db = database.get_connection()
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT workspace_id, user_id, name, created_at
                FROM workspaces
                WHERE workspace_id = %s
            """, (
                str(workspace_id),
            ))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("""
                SELECT video_id
                FROM workspace_videos
                WHERE workspace_id = %s
            """, (str(workspace_id),))

            video_ids = [row[0] for row in cursor.fetchall()]

            workspace = Workspace(
                name = row[2],
                user_id=row[1],
                workspace_id=UUID(row[0]),
                created_at=row[3]
            )

            for video_id in video_ids:
                workspace.add_video_reference(video_id)

            return workspace
        except:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

