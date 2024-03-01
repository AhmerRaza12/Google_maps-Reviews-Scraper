import pandas as pd
import json
from collections import OrderedDict
from datetime import datetime


df = pd.read_excel('reviews.xlsx')

data = OrderedDict()

for index, row in df.iterrows():
    shop_name = row['Shop Name']
    shop_id = row['Shop ID']
    

    reviewer_review = row['Reviewer Review'] if pd.notna(row['Reviewer Review']) else ''
    

    if pd.notna(row['Reviewer Date']):
        reviewer_date = datetime.strptime(str(row['Reviewer Date']), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
    else:
        reviewer_date = ''

    review_data = {
        'reviewer_name': row['Reviewer Name'],
        'reviewer_star': row['Reviewer Star'],
        'reviewer_review_date': reviewer_date,
        'reviewer_review': reviewer_review
    }

    if shop_id in data:

        data[shop_id]['Review Array'].append(review_data)
    else:
        data[shop_id] = {
            'Shop Name': shop_name,
            'Store ID': shop_id,
            'Review Array': [review_data]
        }


output_json = json.dumps(list(data.values()), indent=4, ensure_ascii=False)
with open('reviews.json', 'w', encoding='utf-8') as json_file:
    json_file.write(output_json)

print("Conversion to JSON completed.")
