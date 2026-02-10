@echo off
chcp 65001 >nul
title ดาวน์โหลดฟอนต์ภาษาไทย
echo ============================================
echo 📥 ดาวน์โหลดฟอนต์ภาษาไทย
echo ============================================
echo.

REM สร้างโฟลเดอร์
if not exist "static\fonts" mkdir "static\fonts"

echo 📁 กำลังดาวน์โหลดฟอนต์ Sarabun...
echo -------------------------------------------
curl -L -o "static\fonts\Sarabun-Regular.ttf" "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf" 2>nul
curl -L -o "static\fonts\Sarabun-Medium.ttf" "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf" 2>nul
curl -L -o "static\fonts\Sarabun-Bold.ttf" "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf" 2>nul

echo.
echo 📁 กำลังดาวน์โหลดฟอนต์ Kanit...
echo -------------------------------------------
curl -L -o "static\fonts\Kanit-Regular.ttf" "https://github.com/google/fonts/raw/main/ofl/kanit/Kanit-Regular.ttf" 2>nul
curl -L -o "static\fonts\Kanit-Medium.ttf" "https://github.com/google/fonts/raw/main/ofl/kanit/Kanit-Medium.ttf" 2>nul
curl -L -o "static\fonts\Kanit-Bold.ttf" "https://github.com/google/fonts/raw/main/ofl/kanit/Kanit-Bold.ttf" 2>nul

echo.
echo ============================================
echo ✅ เสร็จสิ้น!
echo ============================================
echo.
echo 📝 หมายเหตุ:
echo - ถ้าดาวน์โหลดไม่ได้ ให้ดาวน์โหลดฟอนต์จาก:
echo   - Sarabun: https://fonts.google.com/specimen/Sarabun
echo   - Kanit: https://fonts.google.com/specimen/Kanit
echo - แล้ววางไฟล์ .ttf ในโฟลเดอร์ static/fonts/
echo.
pause
