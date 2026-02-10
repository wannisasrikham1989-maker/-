# คู่มือตั้งค่า XAMPP/phpMyAdmin สำหรับระบบยืม-คืนครุภัณฑ์

## ขั้นตอนที่ 1: ติดตั้งและตั้งค่า XAMPP

### 1.1 ดาวน์โหลดและติดตั้ง XAMPP
- ดาวน์โหลด XAMPP จาก: https://www.apachefriends.org/download.html
- ติดตั้งในโฟลเดอร์ `C:\xampp` (ค่าเริ่มต้น)

### 1.2 เริ่มต้น Apache และ MySQL
1. เปิด XAMPP Control Panel
2. คลิก **Start** ที่ Apache
3. คลิก **Start** ที่ MySQL

### 1.3 เข้าถึง phpMyAdmin
- เปิดเบราว์เซอร์ ไปที่: http://localhost/phpmyadmin
- หรือคลิกปุ่ม **Admin** ที่ MySQL ใน XAMPP Control Panel

---

## ขั้นตอนที่ 2: ตั้งค่ารหัสผ่าน MySQL (แนะนำ)

### 2.1 เข้า phpMyAdmin
- ไปที่ http://localhost/phpmyadmin
- คลิกเมนู **User accounts**
- ค้นหา user: `root` @ `localhost`
- คลิก **Edit privileges**

### 2.2 เปลี่ยนรหัสผ่าน
- คลินที่แท็บ **Change password**
- ใส่รหัสผ่านใหม่ (หรือเว้นว่างไว้ถ้าไม่ต้องการตั้งรหัส)
- คลิก **Go**

### 2.3 อัพเดท backend.py
เปิดไฟล์ `backend.py` และแก้ไข:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'รหัสผ่านที่ตั้งไว้',  # ถ้าไม่ตั้ง ให้เว้นว่าง ''
    'database': 'equipment_db',
    'port': 3306
}
```

---

## ขั้นตอนที่ 3: ติดตั้ง Python และ Dependencies

### 3.1 ตรวจสอบ Python
```bash
python --version
```
ต้องมี Python 3.7 ขึ้นไป

### 3.2 ติดตั้ง packages
```bash
pip install -r requirements.txt
```

---

## ขั้นตอนที่ 4: นำเข้าฐานข้อมูลจาก phpMyAdmin

### 4.1 นำเข้าฐานข้อมูล
1. ไปที่ **http://localhost/phpmyadmin**
2. สร้างฐานข้อมูลใหม่ชื่อ **`equipment_db`**
3. เลือกฐานข้อมูล `equipment_db`
4. คลิก tab **"Import"**
5. เลือกไฟล์ `database.sql`
6. คลิก **"Go"**

### 4.2 ทดสอบการเชื่อมต่อ
รันคำสั่งนี้เพื่อทดสอบว่าเชื่อมต่อ phpMyAdmin ได้หรือไม่:

```bash
python init_db.py
```

### 4.3 รัน Backend Server
```bash
python backend.py
```

หรือใช้สคริปต์ที่เตรียมไว้:
```bash
run.bat
```

---

## ขั้นตอนที่ 5: เข้าใช้งานระบบ

1. เปิดเบราว์เซอร์ ไปที่: http://localhost:5000
2. หน้าล็อกอินจะแสดงขึ้นมา

### บัญชีทดสอบ:
| บทบาท | ชื่อผู้ใช้ | รหัสผ่าน |
|-------|-----------|----------|
| Admin | admin | password123 |
| User | user1 | password123 |

---

## หมายเหตุทั่วไป

### ปัญหาที่พบบ่อย:

**1. ไม่สามารถเชื่อมต่อ MySQL ได้**
- ตรวจสอบว่า MySQL ใน XAMPP กำลังทำงานอยู่
- ตรวจสอบ port (ปกติ 3306)

**2. ImportError: No module named...**
- รัน `pip install -r requirements.txt` อีกครั้ง

**3. Access denied for user 'root'**
- ตรวจสอบรหัสผ่านใน `DB_CONFIG`
- ลองเว้นรหัสผ่านไว้ว่างถ้าไม่ได้ตั้ง

### การเปลี่ยน Port ของ MySQL:
ถ้า MySQL ใช้ port อื่น ให้แก้ไขใน `backend.py`:
```python
DB_CONFIG = {
    ...
    'port': 3307  # เปลี่ยนเป็น port ที่ใช้
}
```

### การเปลี่ยน Port ของ Flask:
```bash
set FLASK_RUN_PORT=8080
python backend.py
```

---

## การสำรองข้อมูล

ใน phpMyAdmin:
1. เลือกฐานข้อมูล `equipment_db`
2. คลิก **Export**
3. เลือกรูปแบบ SQL
4. คลิก **Go** เพื่อดาวน์โหลด
