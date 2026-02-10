"""
Download Thai Fonts Script
ดาวน์โหลดฟอนต์ภาษาไทยจาก Google Fonts

ฟอนต์ที่ดาวน์โหลด:
- Sarabun (Regular, Medium, Bold)
- Kanit (Regular, Medium, Bold)
"""

import os
import urllib.request
import zipfile

# URL สำหรับดาวน์โหลดฟอนต์
FONTS = {
    'Sarabun': {
        '400': 'https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf',
        '500': 'https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf',
        '700': 'https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf',
    },
    'Kanit': {
        '400': 'https://github.com/google/fonts/raw/main/ofl/kanit/Kanit-Regular.ttf',
        '500': 'https://github.com/google/fonts/raw/main/ofl/kanit/Kanit-Medium.ttf',
        '700': 'https://github.com/google/fonts/raw/main/ofl/kanit/Kanit-Bold.ttf',
    }
}

def create_fonts_folder():
    """สร้างโฟลเดอร์ fonts"""
    fonts_dir = os.path.join('static', 'fonts')
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
        print(f"สร้างโฟลเดอร์: {fonts_dir}")
    return fonts_dir

def download_font(font_name, weight, url):
    """ดาวน์โหลดฟอนต์"""
    filename = f"{font_name}-{weight}.ttf"
    filepath = os.path.join('static', 'fonts', filename)
    
    if os.path.exists(filepath):
        print(f"⏭️ ข้าม (มีอยู่แล้ว): {filename}")
        return True
    
    print(f"⬇️ กำลังดาวน์โหลด: {filename}")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ สำเร็จ: {filename}")
        return True
    except Exception as e:
        print(f"❌ ล้มเหลว: {filename} - {e}")
        return False

def main():
    print("="*50)
    print("📥 ดาวน์โหลดฟอนต์ภาษาไทย")
    print("="*50)
    print()
    
    # สร้างโฟลเดอร์
    fonts_dir = create_fonts_folder()
    
    # ดาวน์โหลดฟอนต์ทั้งหมด
    for font_name, weights in FONTS.items():
        print(f"\n📁 ฟอนต์: {font_name}")
        print("-" * 30)
        for weight, url in weights.items():
            download_font(font_name, weight, url)
    
    print()
    print("="*50)
    print("✅ เสร็จสิ้น!")
    print("="*50)
    print()
    print("หมายเหตุ: ถ้าดาวน์โหลดไม่ได้ ให้ดาวน์โหลดฟอนต์จาก:")
    print("- Sarabun: https://fonts.google.com/specimen/Sarabun")
    print("- Kanit: https://fonts.google.com/specimen/Kanit")
    print()
    print("แล้ววางไฟล์ใน: static/fonts/")

if __name__ == "__main__":
    main()
