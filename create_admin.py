"""สร้าง Admin User ในฐานข้อมูล"""
import mysql.connector
import hashlib

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'equipment_db',
    'port': 3306
}

# ข้อมูล Admin
username = 'admin'
password = 'admin123456'
full_name = 'ผู้ดูแลระบบ'
email = 'admin@example.com'
phone = '0123456789'
department = 'IT'

# Hash รหัสผ่าน
hashed_password = hashlib.sha256(password.encode()).hexdigest()

print(f"Username: {username}")
print(f"Password (raw): {password}")
print(f"Password (hash): {hashed_password}")

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # ลบ admin เก่าถ้ามี
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    
    # เพิ่ม admin ใหม่
    cursor.execute("""
        INSERT INTO users (username, password, full_name, email, phone, department, role)
        VALUES (%s, %s, %s, %s, %s, %s, 'admin')
    """, (username, hashed_password, full_name, email, phone, department))
    
    conn.commit()
    print("✅ สร้าง Admin User สำเร็จ!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Role: admin")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
