
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=True)
    lastname: Mapped[str] = mapped_column(String(80), nullable=True)
    date_created: Mapped[DateTime] = mapped_column(DateTime())
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    fav_planet: Mapped[List["Planets"]] = relationship(secondary='favorites_character', back_populates='user_favorites')
    fav_character: Mapped[List["Character"]] = relationship(secondary='favorites_planet', back_populates='user_favorites')

def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            'name': self.name,
            'suscription_date': self.suscription_date
        }

class Planet(db.Model):
    __tablename__ = 'planet'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    size: Mapped[int] = mapped_column(String(80), nullable=False)
    gravity: Mapped[bool] = mapped_column(String(30), nullable=False)

    user_favorites: Mapped[List["User"] ] = relationship(secondary='favorites_planet', back_populates="fav_planet")
    
    def serialize(self):
         return{
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'grevity': self.gravity
         }
   


class Character(db.Model):
    __tablename__ = 'character'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    birthday: Mapped[str] = mapped_column(String(30), nullable=False)

    user_favorites: Mapped[List["User"]] = relationship(secondary='favorites_character',back_populates="fav_character")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'birthday': self.birthday
        }


Fav_planet = Table(
    'favorites_planet',
    db.metadata,
    Column('planet_id', ForeignKey('planet.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True)
)
Fav_character = Table(
    'favorites_character',
    db.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('character_id', ForeignKey('character.id'), primary_key=True)
)
