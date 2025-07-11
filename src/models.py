from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Text, Date
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import date


db = SQLAlchemy()

# tabla de asociacion para personas favoritos
favorites_characters = db.Table(
    'favorites_characters',
    db.Column('user_id', db.Integer, db.ForeignKey(
        'user.id'), primary_key=True),
    db.Column('characters_id', db.Integer, db.ForeignKey(
        'characters.id'), primary_key=True)
)

# tabla de asociacion para planetas favoritos
favorites_planets = db.Table(
    'favorites_planets',
    db.Column('user_id', db.Integer, db.ForeignKey(
        'user.id'), primary_key=True),
    db.Column('planet_id', db.Integer, db.ForeignKey(
        'planets.id'), primary_key=True)
)

#tabla de asociacion para naves favoritas
favorites_starships = db.Table(
    'favorites_starships',
    db.Column('user_id', db.Integer, db.ForeignKey(
        'user.id'), primary_key=True),
    db.Column('starship_id', db.Integer, db.ForeignKey(
        'starship.id'), primary_key=True)
)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    subcription_date: Mapped[Optional[date]] = mapped_column(Date)

    favorites_characters = db.relationship(
        'Characters',
        secondary=favorites_characters,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )
    favorites_planets = db.relationship(
        'Planets',
        secondary=favorites_planets,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )
    starships_favorites = db.relationship(
            'Starship',
            secondary=favorites_starships,
            backref=db.backref('users', lazy='dynamic'),
            lazy='dynamic'
      )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "subcription_date": self.subcription_date.isoformat() if self.subcription_date else None,
            # do not serialize the password, its a security breach
        }


class Characters(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    species: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    homeworld: Mapped[str] = mapped_column(String(100), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "description": self.description,
            "homeworld": self.homeworld
        }


class Planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    climate: Mapped[str] = mapped_column(String(100), nullable=True)
    terrain: Mapped[str] = mapped_column(String(100), nullable=True)
    population: Mapped[Optional[int]] = mapped_column(nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }

class Starship(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    starship_class: Mapped[str] = mapped_column(String(100), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "starship_class": self.starship_class
        }