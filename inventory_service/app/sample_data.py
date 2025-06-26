import random
from faker import Faker
from datetime import date
from decimal import Decimal
from .db.models import Hotel, Inventory
from sqlalchemy import select

fake = Faker()

hotel_info = [
    {"hotel_name": "Royal Lancaster", "location": "London", "hotel_id": 111, "room_price": 304},
    {"hotel_name": "Shangri-La The Shard", "location": "London", "hotel_id": 222, "room_price": 415},
    {"hotel_name": "Abbots Grange Manor House", "location": "Worcestershire", "hotel_id": 333, "room_price": 310},
    {"hotel_name": "The Gleneagles", "location": "Scotland", "hotel_id": 444, "room_price": 346},
    {"hotel_name": "The Grand", "location": "Brighton", "hotel_id": 555, "room_price": 130},
    {"hotel_name": "St Brides Spa", "location": "Wales", "hotel_id": 666, "room_price": 190},
    {"hotel_name": "Cliveden House", "location": "Berkshire", "hotel_id": 777, "room_price": 280}
]

room_types = [
    "Standard Rooms", "Deluxe Rooms", "Suites", "Penthouse Suites"
]

demand_levels = ["low", "medium", "high"]

def generate_inventory_data():
    data = []
    today = date.today()
    for hotel in hotel_info:
        for room_type in room_types:
            # Assign available rooms based on room type
            if room_type == "Standard Rooms":
                available = random.randint(10, 20)
            elif room_type == "Deluxe Rooms":
                available = random.randint(5, 10)
            elif room_type == "Suites":
                available = random.randint(2, 5)
            elif room_type == "Penthouse Suites":
                available = random.randint(1, 2)
            else:
                available = random.randint(1, 5)
            # Random demand level
            demand = random.choice(demand_levels)
            # Room price can be varied a bit for each type
            base_price = hotel["room_price"]
            if room_type == "Standard Rooms":
                price = Decimal(base_price)
            elif room_type == "Deluxe Rooms":
                price = Decimal(base_price * 1.2)
            elif room_type == "Suites":
                price = Decimal(base_price * 1.5)
            elif room_type == "Penthouse Suites":
                price = Decimal(base_price * 2)
            else:
                price = Decimal(base_price)
            # Round price to 2 decimal places
            price = price.quantize(Decimal("0.01"))
            data.append({
                "hotel_id": hotel["hotel_id"],
                "hotel_name": hotel["hotel_name"],
                "location": hotel["location"],
                "room_type": room_type,
                "date": today,
                "available_rooms": available,
                "room_price": price,
                "demand_level": demand
            })
    return data

async def populate_sample_inventory(session):
    # Only populate if Inventory table is empty
    inventory_count = await session.execute(select(Inventory))
    if inventory_count.scalars().first() is not None:
        return  # Inventory table is not empty, skip population

    # Insert hotels if not already present
    for hotel in hotel_info:
        db_hotel = await session.get(Hotel, hotel["hotel_id"])
        if not db_hotel:
            db_hotel = Hotel(
                hotel_id=hotel["hotel_id"],
                hotel_name=hotel["hotel_name"],
                location=hotel["location"]
            )
            session.add(db_hotel)
    await session.commit()

    # Insert inventory
    data = generate_inventory_data()
    for item in data:
        # Check if inventory already exists
        stmt = select(Inventory).filter_by(
            hotel_id=item["hotel_id"],
            room_type=item["room_type"],
            date=item["date"]
        )
        result = await session.execute(stmt)
        if not result.scalars().first():
            inventory = Inventory(
                hotel_id=item["hotel_id"],
                room_type=item["room_type"],
                date=item["date"],
                available_rooms=item["available_rooms"],
                room_price=item["room_price"],
                demand_level=item["demand_level"]
            )
            session.add(inventory)
    await session.commit()
