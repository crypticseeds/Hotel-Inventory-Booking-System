from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Hotel(Base):
    __tablename__ = "hotel"
    hotel_id = Column(Integer, Identity(start=1), primary_key=True)
    hotel_name = Column(String(100), nullable=False, unique=True)
    location = Column(String(100), nullable=False)

    inventories = relationship("Inventory", back_populates="hotel")


class Inventory(Base):
    __tablename__ = "inventory"

    hotel_id = Column(Integer, ForeignKey("hotel.hotel_id"), nullable=False)
    room_type = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    available_rooms = Column(Integer, nullable=False)
    room_price = Column(Numeric(8, 2), nullable=False)
    demand_level = Column(String(20), nullable=True)

    hotel = relationship("Hotel", back_populates="inventories")

    __table_args__ = (
        Index("ix_inventory_hotel_id_date", "hotel_id", "date"),
        PrimaryKeyConstraint("hotel_id", "room_type", "date"),
    )