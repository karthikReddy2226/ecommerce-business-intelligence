
import pandas as pd
from getpass import getpass
from sqlalchemy import create_engine, URL, text

# 1. Read cleaned dataset
file_path = "data/processed/cleaned_online_retail.csv"

df = pd.read_csv(
    file_path,
    dtype={
        "InvoiceNo": str,
        "StockCode": str
    },
    low_memory=False
)

# 2. Rename columns for SQL
df.columns = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "revenue",
    "year",
    "month",
    "month_name",
    "day",
    "hour",
    "day_name"
]

# 3. Convert data types
df["invoice_date"] = pd.to_datetime(df["invoice_date"])

print("Dataset loaded:", df.shape)

# 4. Get PostgreSQL password securely
password = getpass("Enter PostgreSQL password: ")

# 5. Create database connection
connection_url = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password=password,
    host="localhost",
    port=5432,
    database="ecommerce_db"
)

engine = create_engine(connection_url)

# 6. Upload data to PostgreSQL
print("\nUploading data to PostgreSQL...")

df.to_sql(
    name="online_retail",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=10000
)

# 7. Verify imported data
with engine.connect() as connection:
    result = connection.execute(
        text("SELECT COUNT(*) FROM online_retail")
    )
    row_count = result.scalar()

print("\n========== DATABASE IMPORT SUMMARY ==========")
print("Expected rows:", len(df))
print("Imported rows:", row_count)

if row_count == len(df):
    print("SUCCESS: All records imported!")
else:
    print("WARNING: Imported row count does not match.")

engine.dispose()
