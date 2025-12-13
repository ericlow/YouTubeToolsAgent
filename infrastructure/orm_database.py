
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

load_dotenv()

try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    SessionLocal = sessionmaker(bind=engine)
except OperationalError as e:
    print("\n❌ ERROR: Cannot connect to database")
    print("Make sure PostgreSQL is running:")
    print(f"\nOriginal error: {str(e)}")
    sys.exit(1)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()