from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    Index,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    Computed,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class Booking(Base):
    __tablename__ = "booking"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hotel_id = Column(Integer, ForeignKey("hotel.hotel_id"), nullable=False)
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
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        Index("ix_booking_hotel_id", "hotel_id"),
        Index("ix_booking_arrival_date", "arrival_date"),
    ) 