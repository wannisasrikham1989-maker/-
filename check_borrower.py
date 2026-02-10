"""
ตรวจสอบข้อมูล borrower_id ใน API
รัน: python check_borrower.py
"""
from backend import get_db, session

# จำลอง session สำหรับทดสอบ
class MockSession:
    def __init__(self):
        self.data = {'user_id': 1}

import sys
sys.modules['flask'].session = MockSession()

def check_borrower():
    conn = get_db()
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
