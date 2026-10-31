
import pandas as pd
import os

file_path = "D:\\Data_Analytics_Projects\\ecommerce-business-intelligence\\data\\raw\\Online Retail.xlsx"

if os.path.exists(file_path):
    print("Dataset found successfully!")

    df = pd.read_excel(file_path)

    print("\nDataset Shape:")
    print(df.shape)

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nFirst 5 Records:")
    print(df.head())

    print("\nDataset Information:")
    print(df.info())

else:
    print("Dataset not found!")
    print("Please check the file location.")
