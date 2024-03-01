import pandas as pd
from openpyxl import Workbook

df = pd.read_csv('reviews_3.csv', encoding='utf-8')
excel_file_path = 'rem.xlsx'
wb = Workbook()

ws = wb.active
ws.append(df.columns.tolist())

data = df.values.tolist()

for row in data:
    ws.append(row)

wb.save(excel_file_path)

print(f"CSV file has been converted to Excel file: {excel_file_path}")
