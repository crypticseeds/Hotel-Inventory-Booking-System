# Synthetic Training Data Generator for Hotel Inventory Booking System

This folder contains the script and environment setup to generate synthetic training data for hotel price and demand prediction. The generated data is intended for training AI models that will provide live price and demand ratings, which are then fed into the inventory database to keep hotel booking information up-to-date.

## Contents
- `main.py`: Script to generate a large CSV of synthetic hotel booking data (2024-2025) with realistic features for ML training.
- `pyproject.toml` & `uv.lock`: Project dependencies, managed by [uv](https://docs.astral.sh/uv/).
- `.python-version`: Specifies Python 3.13 for reproducibility.

## Requirements
- [uv](https://docs.astral.sh/uv/) (fast Python package/dependency manager)
- Python 3.13 (automatically managed by uv)

## Quickstart
1. **Install uv** (if not already):
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create environment and install dependencies:**
   ```sh
   uv venv
   uv pip install -e .
   ```
   This will create a `.venv` and install all required packages as per `pyproject.toml` and `uv.lock`.

3. **Run the data generator:**
   ```sh
   uv run main.py
   ```
   This will generate a file at `~/synthetic_hotel_bookings_2024_2025.csv` with 50,000 rows of synthetic booking data.

## Notes
- The script uses [Faker](https://faker.readthedocs.io/), [pandas](https://pandas.pydata.org/), and [numpy](https://numpy.org/) for data generation and manipulation.
- All dependencies are managed via `pyproject.toml` and locked in `uv.lock` for reproducibility.

## Output
- `~/synthetic_hotel_bookings_2024_2025.csv`: The generated dataset, ready for use in AI/ML pipelines.

---
For more on uv workflows, see [uv documentation](https://docs.astral.sh/uv/).
