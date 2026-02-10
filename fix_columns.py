"""
สคริปต์เพิ่ม column ที่ขาดหายไปในฐานข้อมูล
รัน: python fix_columns.py
"""
from backend import get_db

def fix_columns():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # ตรวจสอบว่า column borrower_id มีอยู่หรือไม่
        cursor.execute("SHOW COLUMNS FROM borrow_history LIKE 'borrower_id'")
        if not cursor.fetchone():
            print("➕ เพิ่ม column 'borrower_id' ในตาราง borrow_history...")
            cursor.execute("ALTER TABLE borrow_history ADD COLUMN borrower_id INT DEFAULT NULL AFTER equipment_id")
            print("✅ เพิ่ม 'borrower_id' สำเร็จ!")
        else:
            print("✅ Column 'borrower_id' มีอยู่แล้ว")
        
        # ตรวจสอบว่า column image มีอยู่หรือไม่
        cursor.execute("SHOW COLUMNS FROM equipment LIKE 'image'")
        if not cursor.fetchone():
            print("➕ เพิ่ม column 'image' ในตาราง equipment...")
            cursor.execute("ALTER TABLE equipment ADD COLUMN image VARCHAR(500) DEFAULT NULL AFTER note")
            print("✅ เพิ่ม 'image' สำเร็จ!")
        else:
            print("✅ Column 'image' มีอยู่แล้ว")
        
        conn.commit()
        print("\n🎉 เพิ่ม column ทั้งหมดสำเร็จ!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_columns()
