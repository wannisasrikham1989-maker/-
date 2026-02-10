"""
ตรวจสอบข้อมูล borrower_id ใน API
รัน: python check_borrower.py
"""
import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'equipment_db'
}

def check_borrower():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT e.*, 
               bh.id as borrow_id,
               bh.borrower_id,
               bh.status as borrow_status
        FROM equipment e
        LEFT JOIN borrow_history bh ON e.id = bh.equipment_id 
            AND bh.status = 'กำลังยืม'
        ORDER BY e.id
    """)
    equipment = cursor.fetchall()
    
    print("📋 ข้อมูลครุภัณฑ์จาก API:\n")
    
    for eq in equipment:
        print(f"รหัส: {eq['id']}")
        print(f"ชื่อ: {eq['name']}")
        print(f"สถานะ: {eq['status']}")
        print(f"borrower_id: {eq['borrower_id']}")
        print("-" * 40)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_borrower()
