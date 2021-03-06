from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class DrinkNotification(Base):
    __tablename__ = 'drink_notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    drink_id = Column(Integer, ForeignKey('drinks.id'))
    received = Column(Boolean, default=False)
    datetime = Column(DateTime, default=datetime.now)

    drink = relationship('Drink')