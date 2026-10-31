
import pandas as pd

# Load the original dataset
file_path = "D:\\Data_Analytics_Projects\\ecommerce-business-intelligence\\data\\raw\\Online Retail.xlsx"
df = pd.read_excel(file_path)

print("========== DATASET OVERVIEW ==========")

print("\n1. Dataset Shape:")
print(df.shape)

print("\n2. Column Data Types:")
print(df.dtypes)

print("\n3. Missing Values:")
print(df.isnull().sum())

print("\n4. Duplicate Rows:")
print(df.duplicated().sum())

print("\n5. Statistical Summary:")
print(df.describe())

print("\n6. Cancelled Transactions:")
print(df["InvoiceNo"].astype(str).str.startswith("C").sum())

print("\n7. Negative Quantities:")
print((df["Quantity"] < 0).sum())

print("\n8. Zero or Negative Prices:")
print((df["UnitPrice"] <= 0).sum())

print("\n9. Unique Countries:")
print(df["Country"].nunique())

print("\n10. Unique Customers:")
print(df["CustomerID"].nunique())

print("\n========== EXPLORATION COMPLETED ==========")
