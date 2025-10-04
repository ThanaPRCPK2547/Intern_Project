# Intern_Project — Real-time Stock ETL → BI (5–10 นาที)

มินิโปรเจกต์สำหรับดึงราคาหุ้นจาก **Alpha Vantage**, เก็บลง **MySQL**, ทำกราฟด้วยการใช้ Python เป็นBackendเป็นหลักและแสดงผลบนหน้าเว็บ

## โครงสร้าง (ตามไฟล์ที่มี)
- backend/
  - api.py # ดึง intraday จาก Alpha Vantage → upsert ลง MySQL
  - app.py # ดึง intraday → export เป็น CSV ต่อสัญลักษณ์
  - simple-insert.py # สคริปต์ทดสอบ insert 1 แถวลงตาราง
  - qqqq0.py # ตัวอย่างดึงข้อมูลรายเดือน (monthly) ด้วย pandas
- frontend/
  - web.html # หน้าเว็บสำหรับแสดงกราฟ/ผลลัพธ์
- requirements.txt # ไลบรารีพื้นฐาน (ติดตั้งเพิ่มตามด้านล่างหากจำเป็น)
