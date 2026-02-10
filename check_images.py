"""
ตรวจสอบรูปภาพในฐานข้อมูล
รัน: python check_images.py
"""
from backend import get_db

def check_images():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, name, image FROM equipment ORDER BY id")
    equipment = cursor.fetchall()
    
    print(f"📋 ครุภัณฑ์ทั้งหมด: {len(equipment)} รายการ\n")
    
    for eq in equipment:
        has_image = "✅" if eq['image'] else "❌"
        print(f"{has_image} {eq['id']}: {eq['name']}")
        if eq['image']:
            print(f"   📷 URL: {eq['image'][:80]}...")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_images()
