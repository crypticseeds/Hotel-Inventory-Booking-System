import random
import string

from sqlalchemy import (
    Boolean,
    Column,
    Computed,
    Date,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Booking(Base):
    __tablename__ = "booking"

    def generate_booking_id():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=7))

    booking_id = Column(
        String(7), primary_key=True, default=generate_booking_id, unique=True
    )
    guest_name = Column(String(100), nullable=False)
    hotel_id = Column(Integer, nullable=False)
    arrival_date = Column(Date, nullable=False)
    stay_length = Column(Integer, nullable=False)
    check_out_date = Column(
        Date, Computed("arrival_date + stay_length", persisted=True)
    )
    room_type = Column(String(50), nullable=False)
    adults = Column(Integer, nullable=False)
    children = Column(Integer, nullable=False)
    meal_plan = Column(String(50), nullable=True)
    market_segment = Column(String(50), nullable=True)
    is_weekend = Column(Boolean, nullable=False)
    is_holiday = Column(Boolean, nullable=False)
    booking_channel = Column(String(50), nullable=True)
    room_price = Column(Numeric(8, 2), nullable=False)
    reservation_status = Column(String(20), nullable=False)
    total_price = Column(
        Numeric(10, 2), Computed("room_price * stay_length", persisted=True)
    )
    created_at = Column(Date, server_default=func.current_date())

    __table_args__ = (
        Index("ix_booking_hotel_id", "hotel_id"),
        Index("ix_booking_arrival_date", "arrival_date"),
    )
