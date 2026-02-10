# ระบบยืม-คืนครุภัณฑ์

ระบบบริหารจัดการครุภัณฑ์ ยืม-คืน สำหรับองค์กร

## 🚀 เริ่มต้นใช้งาน

### ข้อกำหนด
- Node.js 18+
- Firebase CLI

### ติดตั้ง
```bash
# ติดตั้ง Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# ติดตั้ง dependencies
npm install
```

### รันโลคัล
```bash
firebase serve
```
เปิด: http://localhost:5000

### Deploy ไป Firebase
```bash
firebase deploy
```

## 📁 โครงสร้างไฟล์

```
├── firebase-login.html       # หน้าเข้าสู่ระบบ
├── firebase-register.html    # ลงทะเบียนผู้ใช้
├── firebase-register-admin.html  # ลงทะเบียนผู้ดูแลระบบ
├── firebase-user.html       # หน้าผู้ใช้ทั่วไป
├── firebase-admin.html      # หน้า Admin Dashboard
├── static/
│   ├── firebase-config.js   # Firebase config
│   ├── firebase-service.js  # Firebase services
│   ├── fonts.css           # ฟอนต์
│   └── favicon.svg         # ไอคอน
├── firestore.rules          # Firestore security rules
├── storage.rules            # Storage security rules
└── firebase.json           # Firebase config
```

## 🔧 ฟีเจอร์

### ผู้ดูแลระบบ (Admin)
- เพิ่ม/แก้ไข/ลบ ครุภัณฑ์
- กรองตามหมวดหมู่, สถานะ
- ดูประวัติการยืม-คืน
- ดูประวัติการขาย

### ผู้ใช้ทั่วไป
- ดูครุภัณฑ์ที่พร้อมยืม
- ยืมครุภัณฑ์
- คืนครุภัณฑ์
- ดูประวัติการยืม-คืน

## 🔐 หมวดหมู่เริ่มต้น
- คอมพิวเตอร์
- เก้าอี้
- โน้ตบุ๊ค

## 📝 หมายเหตุ
- API Key ในไฟล์เป็นของตัวอย่าง ควรสร้าง Firebase project ของตัวเอง
- ควรเปิด Firebase Storage สำหรับอัปโหลดรูปภาพ
