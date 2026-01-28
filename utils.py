"""
Utility functions for the attendance tracking system.
"""

import logging
from datetime import datetime, timedelta


def setup_logging(log_file="attendance.log", level=logging.INFO):
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to log file
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def get_date_string(offset_days=0):
    """
    Get date string in YYYY-MM-DD format.
    
    Args:
        offset_days: Number of days to offset from today (negative for past dates)
    
    Returns:
        Date string in YYYY-MM-DD format
    """
    target_date = datetime.now() + timedelta(days=offset_days)
    return target_date.strftime('%Y-%m-%d')


def get_timestamp():
    """
    Get current timestamp in ISO format.
    
    Returns:
        Timestamp string in ISO format
    """
    return datetime.now().isoformat()


def validate_date_format(date_string):
    """
    Validate that a date string is in YYYY-MM-DD format.
    
    Args:
        date_string: Date string to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_attendance_record(subject_code, present, total):
    """
    Validate attendance record values.
    
    Args:
        subject_code: Subject code string
        present: Present count
        total: Total count
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not subject_code or not isinstance(subject_code, str):
        return False, "Invalid subject code"
    
    if not isinstance(present, int) or present < 0:
        return False, f"Invalid present count: {present}"
    
    if not isinstance(total, int) or total < 0:
        return False, f"Invalid total count: {total}"
    
    if present > total:
        return False, f"Present count ({present}) cannot exceed total count ({total})"
    
    return True, None
