"""
Scraper module for cloud deployment.

Refactored version of fetch_attendance_new.py optimized for serverless/cloud environments.
"""

import os
import sys
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from database_postgres import save_cumulative_attendance, save_daily_attendance
from html_parser import parse_attendance_auto
from attendance_calculator import calculate_daily_attendance
from subjects import SUBJECT_MAP
from utils import get_timestamp

logger = logging.getLogger(__name__)


def get_chrome_options():
    """Configure Chrome options for cloud environment."""
    chrome_options = Options()
    
    # Headless mode for cloud
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    return chrome_options


def run_scraper():
    """
    Run the attendance scraper.
    
    Returns:
        dict: Result with success status and data
    """
    # Get credentials from environment
    username = os.getenv('PORTAL_USERNAME')
    password = os.getenv('PORTAL_PASSWORD')
    login_url = "https://automation.vnrvjiet.ac.in/EduPrime3/VNRVJIET"
    
    if not username or not password:
        raise ValueError("PORTAL_USERNAME and PORTAL_PASSWORD must be set")
    
    driver = None
    
    try:
        # Setup Chrome driver
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        wait = WebDriverWait(driver, 40)
        
        today = str(datetime.now().date())
        extraction_timestamp = get_timestamp()
        
        # Login
        logger.info(f"Opening portal: {login_url}")
        driver.get(login_url)
        
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "xpassword").send_keys(password)
        driver.find_element(By.NAME, "xpassword").send_keys(Keys.ENTER)
        
        # Wait for dashboard
        wait.until(EC.presence_of_element_located((By.ID, "root")))
        logger.info("Login successful")
        
        # Click attendance card
        import time
        time.sleep(5)
        
        attendance_card = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Attendance')]"))
        )
        driver.execute_script("arguments[0].click();", attendance_card)
        logger.info("Clicked attendance card")
        
        # Wait for modal
        wait.until(EC.presence_of_element_located((By.ID, "dynamicModal")))
        time.sleep(5)
        
        # Extract HTML
        modal_body = driver.find_element(By.ID, "dynamicModalBody")
        html_content = modal_body.get_attribute("innerHTML")
        
        # Parse HTML
        logger.info("Parsing attendance HTML...")
        parsed_data = parse_attendance_auto(html_content)
        
        if not parsed_data:
            raise Exception("Failed to parse attendance data")
        
        logger.info(f"Parsed {len(parsed_data)} subjects")
        
        # Build cumulative records
        cumulative_records = []
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
        save_cumulative_attendance(cumulative_records, extraction_timestamp)
        
        # Calculate and save daily attendance
        daily_records = calculate_daily_attendance(cumulative_records, today)
        save_daily_attendance(daily_records)
        
        logger.info("Attendance tracking completed successfully")
        
        return {
            'date': today,
            'subjects_count': len(cumulative_records),
            'timestamp': extraction_timestamp
        }
    
    except Exception as e:
        logger.error(f"Scraper error: {e}")
        raise
    
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")
