
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from logger_config import  getLogger

load_dotenv()
logger = getLogger(__name__)

try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    SessionLocal = sessionmaker(bind=engine)
except OperationalError as e:
    logger.error("\n❌ ERROR: Cannot connect to database")
    logger.error("Make sure PostgreSQL is running:")
    logger.error(f"\nOriginal error: {str(e)}")
    sys.exit(1)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()