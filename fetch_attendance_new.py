"""
Enhanced attendance fetching script with modular architecture.

This script:
1. Logs into the college portal
2. Extracts attendance HTML
3. Parses attendance data
4. Saves cumulative attendance
5. Calculates and saves daily attendance
6. Displays summary with insights
"""

import datetime
import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Import new modular components
from database_postgres import (
    init_db, 
    save_cumulative_attendance, 
    save_daily_attendance,
    get_yesterday_data
)
from html_parser import parse_attendance_auto
from attendance_calculator import (
    calculate_daily_attendance,
    calculate_attendance_percentage,
    calculate_required_attendance,
    calculate_bunkable_classes
)
from subjects import SUBJECT_MAP
from utils import setup_logging, get_timestamp

# Setup logging
logger = setup_logging()

# 🔐 Put your credentials here
USERNAME = "23071A6740"
PASSWORD = "**********"

LOGIN_URL = "https://automation.vnrvjiet.ac.in/EduPrime3/VNRVJIET"

# Initialize database
logger.info("Initializing database...")
init_db()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 40)

today = str(datetime.date.today())
extraction_timestamp = get_timestamp()
cumulative_records = []
html_content = ""

try:
    # Open portal
    logger.info(f"Opening portal: {LOGIN_URL}")
    driver.get(LOGIN_URL)

    # Login
    wait.until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "xpassword").send_keys(PASSWORD)
    driver.find_element(By.NAME, "xpassword").send_keys(Keys.ENTER)

    # Wait for dashboard
    wait.until(EC.presence_of_element_located((By.ID, "root")))
    logger.info("Login successful")

    time.sleep(5)

    # Click Attendance card
    attendance_card = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Attendance')]"))
    )
    driver.execute_script("arguments[0].click();", attendance_card)
    logger.info("Clicked attendance card")

    # Wait for modal
    wait.until(EC.presence_of_element_located((By.ID, "dynamicModal")))
    time.sleep(5)

    # Extract modal HTML
    modal_body = driver.find_element(By.ID, "dynamicModalBody")
    html_content = modal_body.get_attribute("innerHTML")

    # Save HTML for debugging
    with open("debug_modal.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info("Modal HTML saved to debug_modal.html")

except Exception as e:
    logger.error(f"Error during portal interaction: {e}")
    raise

finally:
    driver.quit()
    logger.info("Browser closed")

# Parse HTML using new parser
logger.info("Parsing attendance HTML...")
parsed_data = parse_attendance_auto(html_content)

if not parsed_data:
    logger.error("Failed to parse attendance data. Exiting.")
    exit(1)

logger.info(f"Parsed {len(parsed_data)} subjects")

# Build cumulative records with subject names
for subject_code, present, total in parsed_data:
    subject_name = SUBJECT_MAP.get(subject_code, "Unknown Subject")
    cumulative_records.append((
        today,
        subject_code,
        subject_name,
        present,
        total
    ))

# Save cumulative attendance
logger.info("Saving cumulative attendance...")
save_cumulative_attendance(cumulative_records, extraction_timestamp)

# Calculate daily attendance
logger.info("Calculating daily attendance...")
daily_records = calculate_daily_attendance(cumulative_records, today)

# Save daily attendance
logger.info("Saving daily attendance...")
save_daily_attendance(daily_records)

# Display summary
print("\n" + "="*70)
print(f"📅 ATTENDANCE SUMMARY - {today}")
print("="*70)

print("\n📊 Today's Cumulative Attendance:\n")
for record in cumulative_records:
    date_val, subject_code, subject_name, present, total = record
    percentage = calculate_attendance_percentage(present, total)
    
    print(f"  {subject_name}")
    print(f"    Cumulative: {present}/{total} ({percentage:.1f}%)")
    
    # Calculate insights
    if percentage < 75:
        required = calculate_required_attendance(present, total, 75.0)
        print(f"    ⚠️  Need to attend {required} consecutive classes to reach 75%")
    else:
        bunkable = calculate_bunkable_classes(present, total, 75.0)
        if bunkable > 0:
            print(f"    ✅ Can skip {bunkable} classes while maintaining 75%")
        else:
            print(f"    ✅ At target attendance")
    print()

print("\n📈 Today's Attendance Change:\n")
for record in daily_records:
    date_val, subject_code, subject_name, daily_present, daily_total, cum_present, cum_total = record
    
    if daily_present is not None and daily_total is not None:
        if daily_total > 0:
            daily_pct = calculate_attendance_percentage(daily_present, daily_total)
            print(f"  {subject_name}: +{daily_present}/{daily_total} ({daily_pct:.1f}%)")
        else:
            print(f"  {subject_name}: No classes today")
    else:
        print(f"  {subject_name}: First record (no previous data)")

print("\n" + "="*70)
logger.info("Attendance tracking completed successfully")
