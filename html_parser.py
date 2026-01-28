"""
HTML Parser module for extracting attendance data from college portal.

This module provides robust HTML parsing with error handling for:
- Subject codes
- Cumulative present/total counts
- Malformed or missing data
"""

import logging
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional
from utils import validate_attendance_record

logger = logging.getLogger(__name__)


def parse_attendance_html(html_content: str) -> List[Tuple[str, int, int]]:
    """
    Parse attendance HTML and extract subject data.
    
    Args:
        html_content: HTML content from the attendance modal
    
    Returns:
        List of tuples (subject_code, present, total)
    """
    if not html_content:
        logger.error("Empty HTML content provided")
        return []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        records = []
        
        # Find the table with attendance data
        table = soup.find('table', class_='table')
        
        if not table:
            logger.error("Could not find attendance table in HTML")
            return []
        
        tbody = table.find('tbody')
        if not tbody:
            logger.error("Could not find tbody in attendance table")
            return []
        
        rows = tbody.find_all('tr')
        logger.info(f"Found {len(rows)} rows in attendance table")
        
        for idx, row in enumerate(rows):
            try:
                cols = row.find_all(['th', 'td'])
                
                # Skip header row and total row
                if len(cols) < 3:
                    continue
                
                # First column is subject code (in <th>)
                subject_code = cols[0].get_text(strip=True)
                
                # Skip the "Total" row
                if subject_code.lower() == 'total':
                    continue
                
                # Third column contains cumulative attendance (format: "X / Y")
                cumulative_text = cols[2].get_text(strip=True)
                
                # Validate format
                if '/' not in cumulative_text:
                    logger.warning(f"Row {idx}: Invalid attendance format: {cumulative_text}")
                    continue
                
                # Parse present/total
                parts = cumulative_text.split('/')
                if len(parts) != 2:
                    logger.warning(f"Row {idx}: Could not split attendance: {cumulative_text}")
                    continue
                
                try:
                    present = int(parts[0].strip())
                    total = int(parts[1].strip())
                except ValueError as e:
                    logger.warning(f"Row {idx}: Could not parse numbers from {cumulative_text}: {e}")
                    continue
                
                # Validate the record
                is_valid, error_msg = validate_attendance_record(subject_code, present, total)
                if not is_valid:
                    logger.warning(f"Row {idx}: Validation failed for {subject_code}: {error_msg}")
                    continue
                
                records.append((subject_code, present, total))
                logger.debug(f"Parsed: {subject_code} -> {present}/{total}")
                
            except Exception as e:
                logger.error(f"Error parsing row {idx}: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(records)} attendance records")
        return records
        
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return []


def parse_attendance_from_divs(html_content: str) -> List[Tuple[str, int, int]]:
    """
    Alternative parser for div-based grid layout (used by current fetch_attendance.py).
    
    Args:
        html_content: HTML content from the attendance modal
    
    Returns:
        List of tuples (subject_code, present, total)
    """
    if not html_content:
        logger.error("Empty HTML content provided")
        return []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        records = []
        
        # Find all rows in the modal body
        rows = soup.find_all('div', class_='row')
        logger.info(f"Found {len(rows)} div rows")
        
        for idx, row in enumerate(rows):
            try:
                # Find all column divs
                cols = row.find_all('div', recursive=False)
                
                if len(cols) < 3:
                    continue
                
                subject_code = cols[0].get_text(strip=True)
                attendance_text = cols[2].get_text(strip=True)
                
                # Skip rows without attendance format
                if '/' not in attendance_text:
                    continue
                
                # Parse present/total
                parts = attendance_text.split('/')
                if len(parts) != 2:
                    logger.warning(f"Row {idx}: Could not split attendance: {attendance_text}")
                    continue
                
                try:
                    present = int(parts[0].strip())
                    total = int(parts[1].strip())
                except ValueError as e:
                    logger.warning(f"Row {idx}: Could not parse numbers from {attendance_text}: {e}")
                    continue
                
                # Validate the record
                is_valid, error_msg = validate_attendance_record(subject_code, present, total)
                if not is_valid:
                    logger.warning(f"Row {idx}: Validation failed for {subject_code}: {error_msg}")
                    continue
                
                records.append((subject_code, present, total))
                logger.debug(f"Parsed: {subject_code} -> {present}/{total}")
                
            except Exception as e:
                logger.error(f"Error parsing div row {idx}: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(records)} attendance records from divs")
        return records
        
    except Exception as e:
        logger.error(f"Error parsing HTML divs: {e}")
        return []


def parse_attendance_auto(html_content: str) -> List[Tuple[str, int, int]]:
    """
    Auto-detect and parse attendance data from HTML.
    Tries table-based parsing first, then falls back to div-based parsing.
    
    Args:
        html_content: HTML content from the attendance modal
    
    Returns:
        List of tuples (subject_code, present, total)
    """
    # Try table-based parsing first
    records = parse_attendance_html(html_content)
    
    if records:
        logger.info("Successfully parsed using table-based parser")
        return records
    
    # Fall back to div-based parsing
    logger.info("Table parsing failed, trying div-based parser")
    records = parse_attendance_from_divs(html_content)
    
    if records:
        logger.info("Successfully parsed using div-based parser")
        return records
    
    logger.error("All parsing methods failed")
    return []
