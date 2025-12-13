from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from domain.repositories.user_repository import UserRepository
from infrastructure.orm_database import get_session

router = APIRouter()

# get a user
@router.get("/{user_id}")
def get_user(s:Session = Depends(get_session)):
    user_repository = UserRepository(s)
    user = user_repository.get_user()
    return user


# get all users
@router.get("/")
def get_users(s:Session = Depends(get_session)):
    user_repository = UserRepository(s)
    users = user_repository.get_users()
    return users


# create a user
@router.post("/")
def create_user(s:Session = Depends(get_session)):
    user_repository = UserRepository(s)
    user = user_repository.create_user()
    user_id = user["user_id"]
    created_at = user["created_at"]
    retval = { "user_id": user_id, "created_at": created_at }
    return retval
