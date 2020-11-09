from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import get_db
from app.auth import get_current_user
from app.users import schemas as user_schemas
from . import schemas, crud

router = APIRouter()


@router.get('/', response_model=List[schemas.DrinkSimple])
def get_my_drinks(user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user.drinks


@router.post('/', response_model=schemas.Drink)
def add_drink(drink: schemas.DrinkCreate, user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.add_drink(db, user, drink.glasses)


@router.get('/notifications', response_model=List[schemas.DrinkNotificationSimple])
def get_notifications(user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = crud.get_notifications(db, user)
    return [{
        'user': notification.drink.user,
        'glasses': notification.drink.glasses,
        'datetime': notification.drink.datetime
    } for notification in notifications]