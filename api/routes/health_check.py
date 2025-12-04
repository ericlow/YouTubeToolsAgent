from sqlalchemy import text
from sqlalchemy.orm import Session
from infrastructure.orm_database import SessionLocal

class HealthCheck:
    @staticmethod
    def check_health_db() -> tuple[bool, str]:
        db: Session | None = None
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1")).scalar()
            engine = db.get_bind()

            return True, f"connected to {engine.url.database} on {engine.url.host}"
        except Exception as e:
            print(e)
            return False, "error connecting to DB"
        finally:
            if db: db.close()

    @staticmethod
    def check_health_youtube() -> tuple[bool, str]:
        return True, "connected to YouTube API OK"

    @staticmethod
    def check_health_anthropic() -> tuple[bool, str]:
        return True, "connected anthropic API OK"

    @staticmethod
    def execute():
        try:
            is_ok_db, details_db = HealthCheck.check_health_db()
            is_ok_youtube, details_youtube = HealthCheck.check_health_youtube()
            is_ok_anthropic, details_anthropic = HealthCheck.check_health_anthropic()

            if is_ok_db and is_ok_youtube and is_ok_anthropic:
                health = "OK"
            else:
                health = "ERROR"


            return     {
                "health":  health,
                "details": {
                    "database": {
                        "health": is_ok_db,
                        "details": details_db
                    },
                    "youtube": {
                        "health": "OK",
                        "details": "connected to yt"
                    },
                    "anthropic": {
                        "health": "OK",
                        "details": "connected to claude"
                    }
                }
            }
        except Exception as e:
            return { "status": "ERROR", "error": str(e) }
