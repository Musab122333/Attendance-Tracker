"""
Attendance Calculator module for computing daily attendance from cumulative data.

This module calculates daily attendance changes by comparing today's cumulative
attendance with the previous day's data.
"""

import logging
from typing import List, Tuple, Optional
from database_new import get_previous_day_attendance

logger = logging.getLogger(__name__)


def calculate_daily_attendance(
    today_records: List[Tuple[str, str, int, int]], 
    date: str
) -> List[Tuple[str, str, str, Optional[int], Optional[int], int, int]]:
    """
    Calculate daily attendance from cumulative data.
    
    Args:
        today_records: List of tuples (date, subject_code, subject_name, cumulative_present, cumulative_total)
        date: Date string in YYYY-MM-DD format
    
    Returns:
        List of tuples (date, subject_code, subject_name, daily_present, daily_total, 
                       cumulative_present, cumulative_total)
        
        daily_present and daily_total will be None for first-time records
    """
    daily_records = []
    
    for record in today_records:
        date_val, subject_code, subject_name, cumulative_present, cumulative_total = record
        
        # Get previous day's attendance for this subject
        previous_data = get_previous_day_attendance(subject_code, date_val)
        
        if previous_data:
            prev_present, prev_total = previous_data
            
            # Calculate daily difference
            daily_present = cumulative_present - prev_present
            daily_total = cumulative_total - prev_total
            
            # Validate the calculation
            if daily_present < 0 or daily_total < 0:
                logger.warning(
                    f"Negative daily attendance for {subject_code} on {date_val}: "
                    f"daily_present={daily_present}, daily_total={daily_total}. "
                    f"This might indicate data correction or error."
                )
            
            logger.info(
                f"{subject_code}: Today +{daily_present}/{daily_total} "
                f"(Cumulative: {cumulative_present}/{cumulative_total})"
            )
        else:
            # First record for this subject
            daily_present = None
            daily_total = None
            logger.info(
                f"{subject_code}: First record (Cumulative: {cumulative_present}/{cumulative_total})"
            )
        
        daily_records.append((
            date_val,
            subject_code,
            subject_name,
            daily_present,
            daily_total,
            cumulative_present,
            cumulative_total
        ))
    
    return daily_records


def calculate_attendance_percentage(present: int, total: int) -> float:
    """
    Calculate attendance percentage.
    
    Args:
        present: Number of classes attended
        total: Total number of classes
    
    Returns:
        Attendance percentage (0-100)
    """
    if total == 0:
        return 0.0
    return (present / total) * 100


def calculate_required_attendance(
    current_present: int, 
    current_total: int, 
    target_percentage: float = 75.0
) -> int:
    """
    Calculate how many consecutive classes need to be attended to reach target percentage.
    
    Args:
        current_present: Current number of classes attended
        current_total: Current total number of classes
        target_percentage: Target attendance percentage (default: 75%)
    
    Returns:
        Number of consecutive classes to attend, or -1 if already above target
    """
    current_pct = calculate_attendance_percentage(current_present, current_total)
    
    if current_pct >= target_percentage:
        return -1
    
    # Calculate required attendance
    # Formula: (current_present + x) / (current_total + x) >= target_percentage / 100
    # Solving for x: x >= (target * current_total - 100 * current_present) / (100 - target)
    
    numerator = (target_percentage * current_total) - (100 * current_present)
    denominator = 100 - target_percentage
    
    if denominator == 0:
        return -1
    
    required = numerator / denominator
    return max(0, int(required) + 1)  # Round up


def calculate_bunkable_classes(
    current_present: int, 
    current_total: int, 
    target_percentage: float = 75.0
) -> int:
    """
    Calculate how many classes can be skipped while maintaining target percentage.
    
    Args:
        current_present: Current number of classes attended
        current_total: Current total number of classes
        target_percentage: Target attendance percentage (default: 75%)
    
    Returns:
        Number of classes that can be skipped, or 0 if already at/below target
    """
    current_pct = calculate_attendance_percentage(current_present, current_total)
    
    if current_pct <= target_percentage:
        return 0
    
    # Calculate bunkable classes
    # Formula: (current_present) / (current_total + x) >= target_percentage / 100
    # Solving for x: x <= (100 * current_present / target - current_total)
    
    max_total = (100 * current_present) / target_percentage
    bunkable = max_total - current_total
    
    return max(0, int(bunkable))
