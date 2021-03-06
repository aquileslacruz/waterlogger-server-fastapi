from math import ceil
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import models, schemas

ID_NOT_FOUND = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail='Id not found')
USERNAME_NOT_FOUND = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                   detail='Username not found')
ALREADY_FOLLOWING = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                  detail='Already following')
NOT_FOLLOWING = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail='Not following')

PAGE_ERROR = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail='Page number not allowed')


def get_user(db: Session, username: str):
    return db.query(
        models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()


def modify_user_by_id(db: Session, id: int, data: dict):
    user = db.query(models.User).filter(models.User.id == id).first()
    user.is_admin = data['is_admin']
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(db: Session, id: int):
    db.query(models.User).filter(models.User.id == id).delete()
    db.commit()
    return True

def get_users(db: Session, page: int = 1, limit: int = 100):
    if page < 0:
        raise PAGE_ERROR
    total = db.query(models.User).count()
    max_page = ceil(total / limit)
    if page > 1 and page > max_page:
        raise PAGE_ERROR
    results = db.query(models.User).offset((page-1) * limit).limit(limit).all()
    return total, results, max_page


def search_users(db: Session,
                 user: schemas.User,
                 query: str,
                 skip: int = 0,
                 limit: int = 10):
    return db.query(models.User)\
        .filter(
            models.User.username.startswith(query),
            models.User.id != user.id
        )\
        .offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False):
    from app.auth import get_password_hash

    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          is_admin=is_admin,
                          hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_admin_user(db: Session, user: schemas.UserCreate):
    return create_user(db, user, is_admin=True)


def follow_user(db: Session, user: schemas.User, id: int):
    person = db.query(models.User).filter(models.User.id == id).first()
    if person is None:
        raise ID_NOT_FOUND
    if person in user.following:
        raise ALREADY_FOLLOWING
    user.following.append(person)
    db.commit()
    return True


def unfollow_user(db: Session, user: schemas.User, id: int):
    person = db.query(models.User).filter(models.User.id == id).first()
    if person is None:
        raise ID_NOT_FOUND
    if person not in user.following:
        raise NOT_FOLLOWING
    user.following.remove(person)
    db.commit()
    return True


def add_follow(db: Session, user: schemas.User, follow: str):
    person = db.query(
        models.User).filter(models.User.username == follow).first()
    if person is None:
        raise USERNAME_NOT_FOUND
    if person in user.following:
        raise ALREADY_FOLLOWING
    user.following.append(person)
    db.commit()
    db.refresh(user)
    return user


def remove_follow(db: Session, user: schemas.User, unfollow: str):
    person = db.query(
        models.User).filter(models.User.username == unfollow).first()
    if person is None:
        raise USERNAME_NOT_FOUND
    if person not in user.following:
        raise USERNAME_NOT_FOUND
    user.following.remove(person)
    db.commit()
    db.refresh(user)
    return user


def get_followers(db: Session,
                  user: schemas.User,
                  skip: int = 0,
                  limit: int = 10):
    return db.query(models.User).filter(
        models.User.following.any(id=user.id)).offset(skip).limit(limit).all()
