
import pandas as pd

file_path = "D:\\Data_Analytics_Projects\\ecommerce-business-intelligence\\data\\processed\\cleaned_online_retail.csv"

df = pd.read_csv(
    file_path,
    dtype={"InvoiceNo": str},
    low_memory=False
)

print("========== CLEANED DATASET VALIDATION ==========")

print("\nDataset Shape:")
print(df.shape)

print("\nFirst 5 Records:")
print(df.head())

print("\nColumn Names:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nRevenue Validation:")
print(df["Revenue"].describe())

print("\nMinimum Quantity:")
print(df["Quantity"].min())

print("\nMinimum Unit Price:")
print(df["UnitPrice"].min())

print("\nValidation Completed!")
