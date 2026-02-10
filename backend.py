"""
ระบบยืม-คืนครุภัณฑ์
Backend API สำหรับเชื่อมต่อกับ MySQL
"""

from flask import Flask, request, jsonify, session, send_from_directory, url_for
from flask_cors import CORS
import mysql.connector
import hashlib
from datetime import datetime
import os
import uuid

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your-secret-key-here-change-this'
CORS(app, supports_credentials=True)

# ตั้งค่า session ให้อยู่นาน 7 วัน
app.config['PERMANENT_SESSION_LIFETIME'] = 604800  # 7 วัน = 604800 วินาที
app.config['SESSION_COOKIE_AGE'] = 604800

# โฟลเดอร์เก็บรูปภาพ
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===================================================
# ตั้งค่าการเชื่อมต่อฐานข้อมูล
# ===================================================

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'equipment_db',
    'port': 3306
}

# ===================================================
# ฟังก์ชันเชื่อมต่อฐานข้อมูล
# ===================================================

def get_db():
    """เชื่อมต่อกับ MySQL (phpMyAdmin)"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")
        return None

def test_connection():
    """ทดสอบการเชื่อมต่อฐานข้อมูล"""
    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return True, version
        return False, None
    except Exception as e:
        return False, str(e)

# ===================================================
# ระบบ Login
# ===================================================

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """ตรวจสอบว่าผู้ใช้ล็อกอินอยู่หรือไม่"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'role': session.get('role'),
                'full_name': session.get('full_name')
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/login', methods=['POST'])
def login():
    """เข้าสู่ระบบ"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Hash รหัสผ่าน
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db()
    if not conn:
        return jsonify({'error': 'ไม่สามารถเชื่อมต่อฐานข้อมูล'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, hashed)
    )
    user = cursor.fetchone()
    
    if user:
        # บันทึก session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        })
    else:
        cursor.close()
        conn.close()
        return jsonify({'error': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """ออกจากระบบ"""
    session.clear()
    return jsonify({'success': True})


# ===================================================
# ระบบ Register (สมัครสมาชิก)
# ===================================================

@app.route('/api/register', methods=['POST'])
def register():
    """สมัครสมาชิกใหม่"""
    data = request.json
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    department = data.get('department', '').strip()
    
    # Validation
    if len(username) < 3:
        return jsonify({'error': 'ชื่อผู้ใช้ต้องมีอย่างน้อย 3 ตัวอักษร'}), 400
    if len(password) < 6:
        return jsonify({'error': 'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร'}), 400
    if len(full_name) < 2:
        return jsonify({'error': 'กรุณากรอกชื่อ-นามสกุล'}), 400
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'กรุณากรอกอีเมลให้ถูกต้อง'}), 400
    if len(phone.replace('-', '').replace(' ', '')) < 9:
        return jsonify({'error': 'กรุณากรอกเบอร์โทรให้ถูกต้อง'}), 400
    if not department:
        return jsonify({'error': 'กรุณาเลือกแผนก'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'error': 'ไม่สามารถเชื่อมต่อฐานข้อมูล'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # ตรวจสอบว่าชื่อผู้ใช้ซ้ำหรือไม่
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว'}), 400
        
        # ตรวจสอบว่าอีเมลซ้ำหรือไม่ (ถ้ามี column email)
        try:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'error': 'อีเมลนี้ถูกใช้งานแล้ว'}), 400
        except:
            pass  # ถ้าไม่มี column email ให้ข้าม
        
        # Hash รหัสผ่าน
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # สร้างผู้ใช้ใหม่
        try:
            cursor.execute("""
                INSERT INTO users (username, password, full_name, email, phone, department, role)
                VALUES (%s, %s, %s, %s, %s, %s, 'user')
            """, (username, hashed_password, full_name, email, phone, department))
        except:
            # ถ้าไม่มี column email/phone/department ให้ใช้แบบเดิม
            cursor.execute("""
                INSERT INTO users (username, password, full_name, role, department, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, hashed_password, full_name, 'user', department, phone))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ',
            'user_id': user_id
        })
        
    except mysql.connector.IntegrityError:
        cursor.close()
        conn.close()
        return jsonify({'error': 'ชื่อผู้ใช้หรืออีเมลซ้ำในระบบ'}), 400
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/register-admin', methods=['POST'])
def register_admin():
    """สมัครสมาชิก Admin ใหม่ (ต้องมีรหัสผ่านพิเศษ)"""
    data = request.json
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    department = data.get('department', '').strip()
    admin_code = data.get('admin_code', '').strip()
    
    # ตรวจสอบรหัสผ่านพิเศษ Admin
    ADMIN_SECRET_CODE = 'admin123'
    if admin_code != ADMIN_SECRET_CODE:
        return jsonify({'error': 'รหัสผ่านพิเศษไม่ถูกต้อง'}), 400
    
    # Validation
    if len(username) < 3:
        return jsonify({'error': 'ชื่อผู้ใช้ต้องมีอย่างน้อย 3 ตัวอักษร'}), 400
    if len(password) < 6:
        return jsonify({'error': 'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร'}), 400
    if len(full_name) < 2:
        return jsonify({'error': 'กรุณากรอกชื่อ-นามสกุล'}), 400
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'กรุณากรอกอีเมลให้ถูกต้อง'}), 400
    if len(phone.replace('-', '').replace(' ', '')) < 9:
        return jsonify({'error': 'กรุณากรอกเบอร์โทรให้ถูกต้อง'}), 400
    if not department:
        return jsonify({'error': 'กรุณาเลือกแผนก'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'error': 'ไม่สามารถเชื่อมต่อฐานข้อมูล'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # ตรวจสอบว่าชื่อผู้ใช้ซ้ำหรือไม่
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว'}), 400
        
        # ตรวจสอบว่าอีเมลซ้ำหรือไม่
        try:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'error': 'อีเมลนี้ถูกใช้งานแล้ว'}), 400
        except:
            pass
        
        # Hash รหัสผ่าน
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # สร้างผู้ใช้ Admin ใหม่
        try:
            cursor.execute("""
                INSERT INTO users (username, password, full_name, email, phone, department, role)
                VALUES (%s, %s, %s, %s, %s, %s, 'admin')
            """, (username, hashed_password, full_name, email, phone, department))
        except:
            # ถ้าไม่มี column email/phone/department ให้ใช้แบบเดิม
            cursor.execute("""
                INSERT INTO users (username, password, full_name, role, department, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, hashed_password, full_name, 'admin', department, phone))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'สมัครสมาชิก Admin สำเร็จ! กรุณาเข้าสู่ระบบ',
            'user_id': user_id
        })
        
    except mysql.connector.IntegrityError:
        cursor.close()
        conn.close()
        return jsonify({'error': 'ชื่อผู้ใช้หรืออีเมลซ้ำในระบบ'}), 400
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

# ===================================================
# จัดการครุภัณฑ์
# ===================================================

@app.route('/api/equipment/search', methods=['GET'])
def search_equipment():
    """ค้นหาครุภัณฑ์"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # สร้าง query แบบ dynamic
    sql = "SELECT * FROM equipment WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (name LIKE %s OR id LIKE %s OR brand LIKE %s OR location LIKE %s)"
        like_query = f"%{query}%"
        params.extend([like_query, like_query, like_query, like_query])
    
    if category:
        sql += " AND category = %s"
        params.append(category)
    
    if status:
        sql += " AND status = %s"
        params.append(status)
    
    sql += " ORDER BY id"
    
    cursor.execute(sql, tuple(params))
    equipment = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(equipment)

@app.route('/api/overdue', methods=['GET'])
def get_overdue():
    """ดึงรายการที่เกินกำหนดคืน"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'admin':
        # Admin เห็นทั้งหมด
        cursor.execute("""
            SELECT bh.*, e.name as equipment_name, u.full_name as borrower_name
            FROM borrow_history bh
            LEFT JOIN equipment e ON bh.equipment_id = e.id
            LEFT JOIN users u ON bh.borrower_name = u.full_name
            WHERE bh.status = 'กำลังยืม' 
            AND bh.return_due_date < CURDATE()
            ORDER BY bh.return_due_date ASC
        """)
    else:
        # User เห็นเฉพาะของตนเอง
        cursor.execute("""
            SELECT bh.*, e.name as equipment_name
            FROM borrow_history bh
            LEFT JOIN equipment e ON bh.equipment_id = e.id
            WHERE bh.status = 'กำลังยืม' 
            AND bh.return_due_date < CURDATE()
            AND bh.borrower_name = %s
            ORDER BY bh.return_due_date ASC
        """, (session['full_name'],))
    
    overdue = cursor.fetchall()
    
    # แปลงวันที่
    for o in overdue:
        if o.get('borrow_date'):
            o['borrow_date'] = str(o['borrow_date'])
        if o.get('return_due_date'):
            o['return_due_date'] = str(o['return_due_date'])
    
    cursor.close()
    conn.close()
    
    return jsonify(overdue)

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export ข้อมูลเป็น CSV"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์เข้าถึง'}), 403
    
    export_type = request.args.get('type', 'equipment')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if export_type == 'equipment':
        cursor.execute("SELECT * FROM equipment ORDER BY id")
        data = cursor.fetchall()
        headers = ['รหัส', 'ชื่อ', 'หมวดหมู่', 'ยี่ห้อ', 'สถานะ', 'สถานที่', 'หมายเหตุ']
    elif export_type == 'sales':
        try:
            cursor.execute("SELECT * FROM sales_history ORDER BY sell_date DESC")
            data = cursor.fetchall()
            headers = ['รหัส', 'รหัสครุภัณฑ์', 'ชื่อสินค้า', 'หมวดหมู่', 'ยี่ห้อ', 'ผู้ซื้อ', 'ผู้ขาย', 'วันที่ขาย', 'ราคา', 'สถานะ']
        except:
            data = []
            headers = []
    else:
        cursor.execute("""
            SELECT bh.*, e.name as equipment_name
            FROM borrow_history bh
            LEFT JOIN equipment e ON bh.equipment_id = e.id
            ORDER BY bh.created_at DESC
        """)
        data = cursor.fetchall()
        headers = ['รหัสการยืม', 'รหัสครุภัณฑ์', 'ชื่อครุภัณฑ์', 'ผู้ยืม', 'แผนก', 'เบอร์โทร', 'วันที่ยืม', 'กำหนดคืน', 'วันที่คืนจริง', 'สถานะ', 'หมายเหตุ']
    
    cursor.close()
    conn.close()
    
    # สร้าง CSV
    from io import StringIO
    import csv
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    
    for row in data:
        values = []
        for key in row:
            val = str(row[key]) if row[key] else ''
            values.append(val)
        writer.writerow(values)
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'attachment; filename={export_type}_export.csv'}
    )

@app.route('/api/equipment', methods=['GET'])
def get_equipment():
    """ดึงรายการครุภัณฑ์ทั้งหมด"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # ดึงข้อมูลครุภัณฑ์พร้อมข้อมูลผู้ยืมล่าสุด
    cursor.execute("""
        SELECT e.*, 
               bh.id as borrow_id,
               bh.borrower_id,
               bh.borrower_name,
               bh.status as borrow_status
        FROM equipment e
        LEFT JOIN borrow_history bh ON e.id = bh.equipment_id 
            AND bh.status = 'กำลังยืม'
        ORDER BY e.id
    """)
    equipment = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(equipment)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """ดึงหมวดหมู่ทั้งหมด"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT category FROM equipment ORDER BY category")
    categories = [c['category'] for c in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return jsonify(categories)

@app.route('/api/equipment', methods=['POST'])
def add_equipment():
    """เพิ่มครุภัณฑ์ใหม่ (Admin เท่านั้น)"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์เข้าถึง'}), 403
    
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO equipment (id, name, category, brand, status, location, note, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['id'], data['name'], data['category'], 
            data.get('brand'), data['status'], 
            data.get('location'), data.get('note'), data.get('image')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'เพิ่มครุภัณฑ์สำเร็จ'})
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipment/<equipment_id>', methods=['DELETE'])
def delete_equipment(equipment_id):
    """ลบครุภัณฑ์ (Admin เท่านั้น)"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์เข้าถึง'}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    
    # ตรวจสอบว่ากำลังถูกยืมอยู่หรือไม่
    cursor.execute(
        "SELECT id FROM borrow_history WHERE equipment_id = %s AND status = 'กำลังยืม'",
        (equipment_id,)
    )
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'ไม่สามารถลบได้ ครุภัณฑ์กำลังถูกยืมอยู่'}), 400
    
    cursor.execute("DELETE FROM equipment WHERE id = %s", (equipment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'ลบครุภัณฑ์สำเร็จ'})

@app.route('/api/equipment/<equipment_id>', methods=['PUT'])
def edit_equipment(equipment_id):
    """แก้ไขครุภัณฑ์ (Admin เท่านั้น)"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์เข้าถึง'}), 403
    
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE equipment 
            SET name = %s, category = %s, brand = %s, status = %s, location = %s, note = %s, image = %s
            WHERE id = %s
        """, (
            data['name'], data['category'], 
            data.get('brand'), data['status'],
            data.get('location'), data.get('note'), data.get('image'),
            equipment_id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'แก้ไขครุภัณฑ์สำเร็จ'})
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """อัปโหลดรูปภาพครุภัณฑ์"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์เข้าถึง'}), 403
    
    if 'image' not in request.files:
        return jsonify({'error': 'ไม่พบไฟล์รูปภาพ'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'กรุณาเลือกไฟล์รูปภาพ'}), 400
    
    # ตรวจสอบนามสกุลไฟล์
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'error': 'รองรับเฉพาะไฟล์ PNG, JPG, JPEG, GIF, WEBP'}), 400
    
    # สร้างชื่อไฟล์ใหม่
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # บันทึกไฟล์
    file.save(filepath)
    
    image_url = f"/static/uploads/{filename}"
    
    return jsonify({
        'success': True,
        'image_url': image_url
    })

# ===================================================
# ยืม-คืนครุภัณฑ์
# ===================================================

@app.route('/api/borrow', methods=['POST'])
def borrow_equipment():
    """ยืมครุภัณฑ์"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # ตรวจสอบสถานะครุภัณฑ์
    cursor.execute("SELECT * FROM equipment WHERE id = %s", (data['equipment_id'],))
    equipment = cursor.fetchone()
    
    if not equipment:
        cursor.close()
        conn.close()
        return jsonify({'error': 'ไม่พบครุภัณฑ์'}), 404
    
    if equipment['status'] != 'พร้อมใช้งาน':
        cursor.close()
        conn.close()
        return jsonify({'error': 'ครุภัณฑ์นี้ไม่พร้อมให้ยืม'}), 400
    
    # บันทึกการยืม
    cursor.execute("""
        INSERT INTO borrow_history 
        (equipment_id, borrower_id, borrower_name, department, phone, borrow_date, return_due_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'กำลังยืม')
    """, (
        data['equipment_id'], session['user_id'], session['full_name'], 
        data.get('department', ''), data.get('phone', ''),
        data['borrow_date'], data['return_due_date']
    ))
    
    # อัพเดทสถานะครุภัณฑ์
    cursor.execute(
        "UPDATE equipment SET status = 'ถูกยืม' WHERE id = %s",
        (data['equipment_id'],)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'บันทึกการยืมสำเร็จ'})

@app.route('/api/return/<int:borrow_id>', methods=['PUT'])
def return_equipment(borrow_id):
    """คืนครุภัณฑ์"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # ดึงข้อมูลการยืม
    cursor.execute("SELECT * FROM borrow_history WHERE id = %s", (borrow_id,))
    borrow = cursor.fetchone()
    
    if not borrow:
        cursor.close()
        conn.close()
        return jsonify({'error': 'ไม่พบรายการยืม'}), 404
    
    # อัพเดทการคืน
    cursor.execute("""
        UPDATE borrow_history 
        SET actual_return_date = %s, status = 'คืนแล้ว'
        WHERE id = %s
    """, (data['actual_return_date'], borrow_id))
    
    # อัพเดทสถานะครุภัณฑ์
    cursor.execute(
        "UPDATE equipment SET status = 'พร้อมใช้งาน' WHERE id = %s",
        (borrow['equipment_id'],)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'บันทึกการคืนสำเร็จ'})

@app.route('/api/return-by-equipment/<equipment_id>', methods=['PUT'])
def return_equipment_by_id(equipment_id):
    """คืนครุภัณฑ์โดยใช้ equipment_id"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # ดึงข้อมูลการยืมที่กำลังยืมอยู่
    cursor.execute("""
        SELECT * FROM borrow_history 
        WHERE equipment_id = %s AND status = 'กำลังยืม'
        ORDER BY id DESC LIMIT 1
    """, (equipment_id,))
    borrow = cursor.fetchone()
    
    if not borrow:
        cursor.close()
        conn.close()
        return jsonify({'error': 'ไม่พบรายการยืม'}), 404
    
    # ตรวจสอบว่าเป็นคนยืมจริงๆ
    if borrow['borrower_id'] != session['user_id']:
        cursor.close()
        conn.close()
        return jsonify({'error': 'คุณไม่ใช่ผู้ยืมครุภัณฑ์นี้'}), 403
    
    # อัพเดทการคืน
    cursor.execute("""
        UPDATE borrow_history 
        SET actual_return_date = %s, status = 'คืนแล้ว'
        WHERE id = %s
    """, (data['actual_return_date'], borrow['id']))
    
    # อัพเดทสถานะครุภัณฑ์
    cursor.execute(
        "UPDATE equipment SET status = 'พร้อมใช้งาน' WHERE id = %s",
        (equipment_id,)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'คืนครุภัณฑ์สำเร็จ'})

# ===================================================
# ขายสินค้า (แทนการลบ)
# ===================================================

@app.route('/api/sell', methods=['POST'])
def sell_equipment():
    """ขายครุภัณฑ์ (ลบและบันทึกประวัติการขาย)"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์ขายสินค้า'}), 403
    
    data = request.json
    equipment_id = data.get('equipment_id')
    buyer_name = data.get('buyer_name', '').strip()
    
    if not equipment_id:
        return jsonify({'error': 'กรุณาระบุรหัสครุภัณฑ์'}), 400
    
    if not buyer_name:
        return jsonify({'error': 'กรุณากรอกชื่อผู้ซื้อ'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'error': 'ไม่สามารถเชื่อมต่อฐานข้อมูล'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # ดึงข้อมูลครุภัณฑ์
        cursor.execute("SELECT * FROM equipment WHERE id = %s", (equipment_id,))
        equipment = cursor.fetchone()
        
        if not equipment:
            cursor.close()
            conn.close()
            return jsonify({'error': 'ไม่พบครุภัณฑ์'}), 404
        
        # บันทึกประวัติการขาย
        try:
            cursor.execute("""
                INSERT INTO sales_history 
                (equipment_id, equipment_name, category, brand, buyer_name, seller_name, sell_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), 'ขายแล้ว')
            """, (
                equipment_id, equipment['name'], equipment['category'], 
                equipment['brand'], buyer_name, session['full_name']
            ))
        except mysql.connector.Error:
            # ถ้าไม่มีตาราง sales_history ให้ข้าม
            pass
        
        # ลบครุภัณฑ์
        cursor.execute("DELETE FROM equipment WHERE id = %s", (equipment_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'ขายสินค้าสำเร็จ: {equipment["name"]} ให้ {buyer_name}'
        })
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sales-history', methods=['GET'])
def get_sales_history():
    """ดึงประวัติการขาย"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์เข้าถึง'}), 403
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT * FROM sales_history 
            ORDER BY sell_date DESC, id DESC
        """)
        sales = cursor.fetchall()
        
        # แปลงวันที่
        for s in sales:
            if s.get('sell_date'):
                s['sell_date'] = str(s['sell_date'])
        
        cursor.close()
        conn.close()
        
        return jsonify(sales)
    except:
        cursor.close()
        conn.close()
        return jsonify([])

@app.route('/api/borrow-history', methods=['GET'])
def get_borrow_history():
    """ดึงประวัติการยืม"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'admin':
        # Admin เห็นทั้งหมด
        cursor.execute("""
            SELECT bh.*, e.name as equipment_name
            FROM borrow_history bh
            LEFT JOIN equipment e ON bh.equipment_id = e.id
            ORDER BY bh.created_at DESC
        """)
    else:
        # User เห็นเฉพาะของตนเอง
        cursor.execute("""
            SELECT bh.*, e.name as equipment_name
            FROM borrow_history bh
            LEFT JOIN equipment e ON bh.equipment_id = e.id
            WHERE bh.borrower_name = %s
            ORDER BY bh.created_at DESC
        """, (session['full_name'],))
    
    history = cursor.fetchall()
    
    # แปลงวันที่เป็น string
    for h in history:
        if h.get('borrow_date'):
            h['borrow_date'] = str(h['borrow_date'])
        if h.get('return_due_date'):
            h['return_due_date'] = str(h['return_due_date'])
        if h.get('actual_return_date'):
            h['actual_return_date'] = str(h['actual_return_date'])
    
    cursor.close()
    conn.close()
    
    return jsonify(history)

@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """สถิติสำหรับ Dashboard"""
    if 'user_id' not in session:
        return jsonify({'error': 'กรุณาเข้าสู่ระบบ'}), 401
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # นับครุภัณฑ์
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'พร้อมใช้งาน' THEN 1 ELSE 0 END) as available,
            SUM(CASE WHEN status = 'ถูกยืม' THEN 1 ELSE 0 END) as borrowed,
            SUM(CASE WHEN status = 'ซ่อมบำรุง' THEN 1 ELSE 0 END) as maintenance
        FROM equipment
    """)
    stats = cursor.fetchone()
    
    # รายการที่กำลังยืม
    cursor.execute("""
        SELECT bh.*, e.name as equipment_name
        FROM borrow_history bh
        LEFT JOIN equipment e ON bh.equipment_id = e.id
        WHERE bh.status = 'กำลังยืม'
        ORDER BY bh.return_due_date ASC
    """)
    current_borrows = cursor.fetchall()
    
    # แปลงวันที่
    for b in current_borrows:
        if b.get('borrow_date'):
            b['borrow_date'] = str(b['borrow_date'])
        if b.get('return_due_date'):
            b['return_due_date'] = str(b['return_due_date'])
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'stats': stats,
        'current_borrows': current_borrows
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """ดึงรายชื่อผู้ใช้ (Admin เท่านั้น)"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์เข้าถึง'}), 403
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, full_name, role, department, phone FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def add_user():
    """เพิ่มผู้ใช้ใหม่ (Admin เท่านั้น)"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'ไม่มีสิทธิ์เข้าถึง'}), 403
    
    data = request.json
    hashed = hashlib.sha256(data['password'].encode()).hexdigest()
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (username, password, full_name, role, department, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['username'], hashed, data['full_name'],
            data['role'], data.get('department'), data.get('phone')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'เพิ่มผู้ใช้สำเร็จ'})
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500


# Serve frontend files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/', defaults={'path': 'login.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    safe_path = os.path.normpath(os.path.join(BASE_DIR, path))
    if not safe_path.startswith(BASE_DIR):
        return jsonify({'error': 'Invalid path'}), 400
    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        return send_from_directory(BASE_DIR, path)
    return jsonify({'error': 'Not found'}), 404

# ===================================================
# เริ่มต้นระบบ
# ===================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏢 ระบบตรวจสอบและยืมครุภัณฑ์")
    print("="*60)
    
    print("\n📊 กำลังเชื่อมต่อฐานข้อมูล phpMyAdmin...")
    success, result = test_connection()
    if success:
        print(f"✅ เชื่อมต่อฐานข้อมูลสำเร็จ! (MySQL {result})")
    else:
        print(f"❌ ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {result}")
        print("กรุณาตรวจสอบว่า XAMPP/MySQL กำลังทำงานอยู่")
        print("และฐานข้อมูล equipment_db มีอยู่ใน phpMyAdmin แล้ว")
        exit(1)
    
    print("\n👥 บัญชีสำหรับเข้าสู่ระบบ:")
    print("\n   👨‍💼 Admin:")
    print("      Username: admin")
    print("      Password: password123")
    print("\n   👤 User:")
    print("      Username: user1") 
    print("      Password: password123")
    print("\n" + "="*60)
    print("🌐 เปิดเว็บไซต์ที่: http://localhost:5000")
    print("💾 ฐานข้อมูล: MySQL (equipment_db) - จาก phpMyAdmin")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
