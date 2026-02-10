"""
อัพเดท borrower_id ในข้อมูลการยืมเก่า
รัน: python fix_borrower_id.py
"""
import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'equipment_db'
}

def fix_borrower_id():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # ดึงข้อมูล users ทั้งหมด
    cursor.execute("SELECT id, username, full_name FROM users")
    users = cursor.fetchall()
    user_map = {u['full_name']: u['id'] for u in users}
    
    print("📋 User map:", user_map)
    
    # ดึงข้อมูล borrow_history ที่ borrower_id เป็น NULL
    cursor.execute("""
        SELECT id, borrower_name, equipment_id 
        FROM borrow_history 
        WHERE borrower_id IS NULL
    """)
    borrows = cursor.fetchall()
    
    print(f"\n🔧 พบ {len(borrows)} รายการที่ต้องอัพเดท\n")
    
    updated = 0
    for b in borrows:
        borrower_name = b['borrower_name']
        if borrower_name in user_map:
            user_id = user_map[borrower_name]
            cursor.execute("""
                UPDATE borrow_history 
                SET borrower_id = %s 
                WHERE id = %s
            """, (user_id, b['id']))
            print(f"✅ อัพเดท: {b['equipment_id']} -> user_id: {user_id}")
            updated += 1
        else:
            print(f"❌ ไม่พบ user: {borrower_name}")
    
    conn.commit()
    print(f"\n🎉 อัพเดทสำเร็จ {updated} รายการ")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_borrower_id()
