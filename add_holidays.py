import json
import os

INPUT_FILE = 'final_data_for_powerbi.json'
OUTPUT_FILE = 'final_data_for_powerbi.json'

def is_in_holiday_period(date_str):
    if not date_str:
        return "Onbekend"
    
    dt = date_str[:10] # Pak het YYYY-MM-DD deel
    
    # Gecombineerde vakantieperiodes NL, BE, DE (NRW) 2017-2025
    holidays = [
        # 2017
        ('2017-02-18', '2017-03-05'), ('2017-04-03', '2017-04-30'), ('2017-07-01', '2017-09-03'),
        ('2017-10-14', '2017-11-05'), ('2017-12-23', '2018-01-07'),
        # 2018
        ('2018-02-10', '2018-02-25'), ('2018-03-26', '2018-05-06'), ('2018-07-01', '2018-09-02'),
        ('2018-10-13', '2018-11-04'), ('2018-12-21', '2019-01-06'),
        # 2019
        ('2019-02-16', '2019-03-10'), ('2019-04-08', '2019-05-05'), ('2019-07-01', '2019-09-01'),
        ('2019-10-12', '2019-11-03'), ('2019-12-21', '2020-01-06'),
        # 2020
        ('2020-02-15', '2020-03-01'), ('2020-04-06', '2020-05-03'), ('2020-06-29', '2020-08-31'),
        ('2020-10-10', '2020-11-15'), ('2020-12-19', '2021-01-06'),
        # 2021
        ('2021-02-13', '2021-02-28'), ('2021-03-29', '2021-05-14'), ('2021-07-01', '2021-09-05'),
        ('2021-10-11', '2021-11-07'), ('2021-12-24', '2022-01-09'),
        # 2022
        ('2022-02-19', '2022-03-06'), ('2022-04-04', '2022-05-08'), ('2022-06-27', '2022-09-04'),
        ('2022-10-04', '2022-11-06'), ('2022-12-23', '2023-01-08'),
        # 2023
        ('2023-02-18', '2023-03-05'), ('2023-04-03', '2023-05-07'), ('2023-06-22', '2023-09-03'),
        ('2023-10-02', '2023-11-05'), ('2023-12-21', '2024-01-07'),
        # 2024
        ('2024-02-10', '2024-02-25'), ('2024-04-27', '2024-05-05'), ('2024-07-06', '2024-09-01'),
        ('2024-10-14', '2024-11-03'), ('2024-12-21', '2025-01-05'),
        # 2025
        ('2025-02-15', '2025-03-09'), ('2025-04-07', '2025-05-04'), ('2025-07-01', '2025-08-31'),
        ('2025-10-11', '2025-11-02'), ('2025-12-20', '2026-01-06')
    ]
    
    for start, end in holidays:
        if start <= dt <= end:
            return "Vakantie"
    return "Buiten vakantie"

def add_holiday_data():
    print("Vakantiegegevens toevoegen aan dataset...")
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} niet gevonden.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for review in data['reviews']:
        review['periode_type'] = is_in_holiday_period(review.get('createTime'))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Check voltooid. Vakantie-labels toegevoegd aan {len(data['reviews'])} zinnen.")

if __name__ == "__main__":
    add_holiday_data()