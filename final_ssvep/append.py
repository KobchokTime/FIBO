import pandas as pd

# อ่านข้อมูลจากไฟล์ CSV
csv_file = 'data.csv'
df = pd.read_csv(csv_file)

# สร้าง DataFrame สำหรับข้อมูลใหม่
new_data = {
    'name': ['Alice'],
    'age': [28],
    'salary': [55000]
}
new_row = pd.DataFrame(new_data)

# เพิ่มข้อมูลใหม่ลงใน DataFrame
df = df._append(new_row, ignore_index=True)

# บันทึก DataFrame ที่มีข้อมูลใหม่ลงในไฟล์ CSV
df.to_csv(csv_file, index=False)

print("เพิ่มข้อมูลลง CSV เรียบร้อยแล้ว")
