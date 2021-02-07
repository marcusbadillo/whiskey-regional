#!/usr/bin/env python
""" create_db.py:  Uses SQLAlchemy to create the sqlite database and
    class models.
"""
# Column types used in app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

# Construct a base class for declarative class definitions
from sqlalchemy.ext.declarative import declarative_base

# For building relationship between two mapped classes
# There are implicit contructs (ex. "save-update") when using relationship()
# See Cascades - http://docs.sqlalchemy.org/en/rel_1_1/orm/cascades.html
from sqlalchemy.orm import relationship

# home base for the actual database and its DBAPI
from sqlalchemy import create_engine

import datetime

# Construct a base class for declarative class definitions.
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Region(Base):
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Whiskey(Base):
    __tablename__ = 'whiskey'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    img_name = Column(String(100))
    description = Column(String(450))
    type = Column(String(250), nullable=False)
    date_added = Column(DateTime, default=datetime.datetime.now)
    manufacturer = Column(String(250), nullable=False)
    abv = Column(String(10), nullable=False)
    proof = Column(String(10))
    region_id = Column(Integer, ForeignKey('region.id', ondelete="CASCADE"))
    region = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, cascade="delete")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'img_name': self.img_name,
            'description': self.description,
            'manufacturer': self.manufacturer,
            'abv': self.abv,
            'proof': self.proof,
            'type': self.type,
            'region': self.region
        }


engine = create_engine('sqlite:///whiskey_regions.db')

Base.metadata.create_all(engine)
