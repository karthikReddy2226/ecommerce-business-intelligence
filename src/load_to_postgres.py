
from pathlib import Path
import tomllib

import pandas as pd
from sqlalchemy import create_engine, text


# Project folders
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = BASE_DIR / "data" / "processed" / "cleaned_online_retail.csv"
SECRETS_FILE = BASE_DIR / ".streamlit" / "secrets.toml"


def main():
    # Check required files
    if not DATA_FILE.exists():
        print("Error: Cleaned dataset not found.")
        print(DATA_FILE)
        return

    if not SECRETS_FILE.exists():
        print("Error: secrets.toml not found.")
        return

    # Read Neon connection string securely
    with open(SECRETS_FILE, "rb") as file:
        secrets = tomllib.load(file)

    database_url = secrets["postgres"]["url"].strip()

    # Use psycopg 3 driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    # Connect to Neon
    engine = create_engine(
        database_url,
        pool_pre_ping=True
    )

    try:
        print("Reading cleaned dataset...")

        df = pd.read_csv(
            DATA_FILE,
            dtype={"InvoiceNo": str},
            low_memory=False
        )

        
# Rename columns to match the dashboard SQL queries
        df.rename(columns={
            "InvoiceNo": "invoice_no",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "UnitPrice": "unit_price",
            "CustomerID": "customer_id",
            "Country": "country",
            "Revenue": "revenue",
            "Year": "year",
            "Month": "month",
            "MonthName": "month_name",
            "Day": "day",
            "Hour": "hour",
            "DayName": "day_name"
        }, inplace=True)


        print("Dataset loaded successfully.")
        print("Rows:", len(df))
        print("Columns:", len(df.columns))

        print("\nUploading data to Neon PostgreSQL...")
        
        df.to_sql(
            "online_retail",
            engine,
            if_exists="replace",
            index=False,
            chunksize=5000
        )

        print("Upload completed!")

        # Verify uploaded records
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT COUNT(*) FROM online_retail")
            )
            total_rows = result.scalar()

        print("\nCloud database verification")
        print("---------------------------")
        print("Uploaded rows:", total_rows)

        if total_rows == len(df):
            print("SUCCESS: All records uploaded correctly!")
        else:
            print("WARNING: Uploaded row count does not match.")

    except Exception as error:
        print("\nDatabase upload failed.")
        print("Error:", error)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
