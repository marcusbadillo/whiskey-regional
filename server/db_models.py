import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

# Base class for all models using SQLAlchemy ORM
Base = declarative_base()


# ----------------------
# User Model Definition
# ----------------------
class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    picture: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    # Relationships
    whiskeys: Mapped[list["Whiskey"]] = relationship(
        "Whiskey", back_populates="user", cascade="all, delete"
    )
    regions: Mapped[list["Region"]] = relationship(
        "Region", back_populates="user", cascade="all, delete"
    )

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "picture": self.picture,
        }


# ------------------------
# Region Model Definition
# ------------------------
class Region(Base):
    __tablename__ = 'region'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped["User"] = relationship("User", back_populates="regions")

    whiskeys: Mapped[list["Whiskey"]] = relationship(
        "Whiskey", back_populates="region", cascade="all, delete"
    )

    def __repr__(self):
        return f"<Region(name='{self.name}')>"

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }


# -------------------------
# Whiskey Model Definition
# -------------------------
class Whiskey(Base):
    __tablename__ = 'whiskey'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    img_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(450), nullable=True)
    type: Mapped[str] = mapped_column(String(250), nullable=False)
    date_added: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    manufacturer: Mapped[str] = mapped_column(String(250), nullable=False)
    abv: Mapped[str] = mapped_column(String(10), nullable=False)
    proof: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    region_id: Mapped[int] = mapped_column(ForeignKey('region.id', ondelete="CASCADE"))
    region: Mapped["Region"] = relationship("Region", back_populates="whiskeys")

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped["User"] = relationship("User", back_populates="whiskeys")

    def __repr__(self):
        return f"<Whiskey(name='{self.name}', abv='{self.abv}', type='{self.type}')>"

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'img_name': self.img_name,
            'description': self.description,
            'manufacturer': self.manufacturer,
            'abv': self.abv,
            'proof': self.proof,
            'type': self.type,
            'region': self.region.name if self.region else None,
        }
