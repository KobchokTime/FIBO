import pandas as pd

# สร้างข้อมูลตัวอย่าง
data = {
    'name': [],
    'age': [],
    'salary': []
}

# สร้าง DataFrame จากข้อมูล
df = pd.DataFrame(data)

# ระบุชื่อไฟล์ CSV ที่ต้องการจะเขียน
csv_file = 'data.csv'

# เขียนข้อมูลลง CSV
df.to_csv(csv_file, index=False)

print("success")

