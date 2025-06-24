import pandas as pd
import random
from faker import Faker
from datetime import date

# Constants and reinitialisation
fake = Faker()
n_rows = 50000

hotel_info = [
    {
        "hotel_name": "Royal Lancaster",
        "location": "London",
        "id": 111,
        "price_estimate": 304,
    },
    {
        "hotel_name": "Shangri-La The Shard",
        "location": "London",
        "id": 222,
        "price_estimate": 415,
    },
    {
        "hotel_name": "Abbots Grange Manor House",
        "location": "Worcestershire",
        "id": 333,
        "price_estimate": 310,
    },
    {
        "hotel_name": "The Gleneagles",
        "location": "Scotland",
        "id": 444,
        "price_estimate": 346,
    },
    {
        "hotel_name": "The Grand",
        "location": "Brighton",
        "id": 555,
        "price_estimate": 130,
    },
    {
        "hotel_name": "St Brides Spa",
        "location": "Wales",
        "id": 666,
        "price_estimate": 190,
    },
    {
        "hotel_name": "Cliveden House",
        "location": "Berkshire",
        "id": 777,
        "price_estimate": 280,
    },
]

room_types = ["Standard Rooms", "Deluxe Rooms", "Suites", "Penthouse Suites"]
market_segments = ["Direct", "Online TA", "Corporate", "Groups"]
meal_plans = ["BB", "HB", "FB", "SC"]
booking_channels = ["Mobile", "Website", "Travel Agent"]
reservation_statuses = ["Check-Out", "Canceled", "No-Show"]

start_date = date(2024, 1, 1)
end_date = date(2025, 12, 31)


# Booking generator
def generate_booking_adjusted():
    hotel = random.choice(hotel_info)
    arrival = fake.date_between(start_date=start_date, end_date=end_date)
    is_weekend = arrival.weekday() >= 5
    is_holiday = arrival.month in [12, 7, 8]
    stay_length = random.randint(1, 7)
    adr = round(random.gauss(hotel["price_estimate"], 40), 2)
    adr = max(60, min(adr, 600))
    demand_level = "low" if adr < 150 else "medium" if adr < 300 else "high"
    children = random.choices(
        [0, 1, 2], weights=[0.85, 0.1, 0.05] if not is_holiday else [0.6, 0.25, 0.15]
    )[0]

    return {
        "booking_id": fake.bothify(text="??#####??"),
        "hotel_name": hotel["hotel_name"],
        "location": hotel["location"],
        "hotel_id": hotel["id"],
        "arrival_date": arrival.isoformat(),
        "lead_time": random.randint(0, 365),
        "stay_length": stay_length,
        "adults": random.randint(1, 4),
        "children": children,
        "room_type": random.choice(room_types),
        "meal_plan": random.choice(meal_plans),
        "market_segment": random.choice(market_segments),
        "is_weekend": is_weekend,
        "is_holiday": is_holiday,
        "booking_channel": random.choice(booking_channels),
        "room_price": round(random.uniform(60, 550), 2),
        "adr": adr,
        "demand_level": demand_level,
        "reservation_status": random.choice(reservation_statuses),
    }


# Generate and save dataset
dataset = [generate_booking_adjusted() for _ in range(n_rows)]
df = pd.DataFrame(dataset)
file_path = "~/synthetic_hotel_bookings_2024_2025.csv"
df.to_csv(file_path, index=False)
