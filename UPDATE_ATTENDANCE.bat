@echo off
REM Quick Attendance Update Script
REM Double-click this file to fetch latest attendance

echo.
echo ========================================
echo   Attendance Tracker - Quick Update
echo ========================================
echo.
echo Fetching latest attendance from portal...
echo This will take about 30-60 seconds.
echo.

REM Set DATABASE_URL for cloud database
set DATABASE_URL=postgresql://attendance_db_6b0v_user:IE1bb8P3u6TZkTyUHGbAVZwj4pQRtwH6@dpg-d5sqa2koud1c73afc90g-a.oregon-postgres.render.com:5432/attendance_db_6b0v

REM Run the scraper
python fetch_attendance_new.py

echo.
echo ========================================
echo   Done!
echo ========================================
echo.
echo Your attendance has been updated!
echo Refresh your Netlify site to see the latest data.
echo.
pause
