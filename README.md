# ระบบยืม-คืนครุภัณฑ์ (Equipment Borrowing System)

ไฟล์สำคัญ:

- `backend.py` - Flask backend ที่เชื่อมต่อ MySQL (ใช้งานร่วมกับ phpMyAdmin)
- `login.html` - หน้าเข้าสู่ระบบ
- `admin.html` - แผงควบคุมสำหรับผู้ดูแล
- `user.html` - หน้าใช้งานสำหรับผู้ใช้ทั่วไป
- `requirements.txt` - ไลบรารี Python ที่ต้องติดตั้ง

การติดตั้งและรัน (Windows / XAMPP หรือ MySQL ที่มี phpMyAdmin):

1. สร้างฐานข้อมูลด้วย `phpMyAdmin` หรือรันสคริปต์ในโค้ด — หากต้องการนำเข้า SQL ด้วยตนเอง ให้สร้างฐานข้อมูลชื่อ `equipment_db` แล้ว import schema ตามต้องการ.

2. แก้ไขการตั้งค่าเชื่อมต่อฐานข้อมูลใน `backend.py` (ตัวแปร `DB_CONFIG`) ให้ตรงกับระบบของคุณ (host, user, password, database, port).

3. ติดตั้ง dependencies (แนะนำให้ใช้ virtualenv):

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

4. รัน backend:

```powershell
python backend.py
```

เมื่อรันครั้งแรก `backend.py` จะสร้างฐานข้อมูลและตารางอัตโนมัติ (หากยังไม่มี) และเพิ่มบัญชีตัวอย่าง:

- Admin: `admin` / `password123`
- User: `user1` / `password123`

5. เปิดหน้าเว็บในเบราว์เซอร์:

- `login.html` เพื่อเข้าสู่ระบบ
- หลังล็อกอินเป็น Admin จะไปที่ `admin.html` และผู้ใช้ปกติจะไปที่ `user.html`

หมายเหตุ:

- ระบบ backend ใช้ session cookie — หากหน้าเว็บถูกให้บริการจากโดเมนอื่น ให้แน่ใจว่า `fetch` ส่ง `credentials: 'include'` และ `backend.py` อนุญาต CORS สำหรับ origin นั้น (ปัจจุบันใช้ `flask_cors.CORS(app, supports_credentials=True)`).
- หากต้องการใช้ phpMyAdmin เพื่อดู/จัดการฐานข้อมูล ให้ใช้ข้อมูลการเชื่อมต่อเดียวกับที่ตั้งค่าใน `backend.py`.

ถ้าต้องการ ฉันสามารถ:

- ปรับปรุง UI เพิ่มฟอร์มแก้ไข/ส่งออกข้อมูล
- ทำระบบอัพโหลดรูปครุภัณฑ์
- ติดตั้งระบบแจ้งเตือนอีเมล/Line
