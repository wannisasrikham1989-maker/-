"""สร้างตาราง sales_history ในฐานข้อมูล"""
import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'equipment_db',
    'port': 3306
}

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    # สร้างตาราง sales_history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            equipment_id VARCHAR(50) NOT NULL,
            equipment_name VARCHAR(200) NOT NULL,
            category VARCHAR(100),
            brand VARCHAR(100),
            buyer_name VARCHAR(200) NOT NULL,
            seller_name VARCHAR(200),
            sell_date DATE NOT NULL,
            price DECIMAL(10,2),
            notes TEXT,
            status VARCHAR(50) DEFAULT 'ขายแล้ว',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("✅ สร้างตาราง sales_history สำเร็จ!")
    
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
finally:
    cursor.close()
    conn.close()
