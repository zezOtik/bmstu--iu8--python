import random
from datetime import datetime, timedelta
import csv
import os

courses = [
    'Python for Beginners',
    'Data Science Fundamentals',
    'Web Development with Flask',
    'Machine Learning Basics',
    'SQL Masterclass'
]
start_date = datetime(2025, 4, 1)
end_date = datetime(2025, 6, 30)

data = []
for _ in range(2000):
    user_id = random.randint(1, 500)
    course_name = random.choice(courses)
    days_diff = (end_date - start_date).days
    random_days = random.randint(0, days_diff)
    completion_date = start_date + timedelta(days=random_days)
    data.append((user_id, course_name, completion_date.date()))

output_file = "input_data/input_data.csv"

os.makedirs("input_data", exist_ok=True)

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['user_id', 'course_name', 'completion_date'])
    writer.writerows(data)

print(f"Успешно сгенерировано {len(data)} строк и сохранено в {output_file}")
