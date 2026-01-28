"""
Enhanced database module for attendance tracking system.

This module provides:
- Improved schema with primary keys and indexes
- Separate tables for cumulative and daily attendance
- Transaction management and error handling
- Query helpers for data analysis
"""

import sqlite3
import logging
from typing import List, Tuple, Optional, Dict
from utils import get_timestamp

logger = logging.getLogger(__name__)

DB_NAME = "attendance.db"


def get_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize database with enhanced schema.
    Creates tables with proper constraints and indexes.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Create cumulative attendance table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS cumulative_attendance (
            date TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            cumulative_present INTEGER NOT NULL,
            cumulative_total INTEGER NOT NULL,
            extraction_timestamp TEXT NOT NULL,
            PRIMARY KEY (date, subject_code)
        )
        """)
        
        # Create daily attendance table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_attendance (
            date TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            daily_present INTEGER,
            daily_total INTEGER,
            cumulative_present INTEGER NOT NULL,
            cumulative_total INTEGER NOT NULL,
            PRIMARY KEY (date, subject_code)
        )
        """)
        
        # Create indexes for performance
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_cumulative_date 
        ON cumulative_attendance(date)
        """)
        
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_cumulative_subject 
        ON cumulative_attendance(subject_code)
        """)
        
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_daily_date 
        ON daily_attendance(date)
        """)
        
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_daily_subject 
        ON daily_attendance(subject_code)
        """)
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def save_cumulative_attendance(records: List[Tuple], extraction_timestamp: str = None):
    """
    Save cumulative attendance records.
    Uses INSERT OR REPLACE to handle duplicates gracefully.
    
    Args:
        records: List of tuples (date, subject_code, subject_name, present, total)
        extraction_timestamp: Timestamp of extraction (defaults to current time)
    """
    if not records:
        logger.warning("No records to save")
        return
    
    if extraction_timestamp is None:
        extraction_timestamp = get_timestamp()
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Add extraction timestamp to each record
        records_with_timestamp = [
            (*record, extraction_timestamp) for record in records
        ]
        
        cur.executemany("""
            INSERT OR REPLACE INTO cumulative_attendance 
            (date, subject_code, subject_name, cumulative_present, cumulative_total, extraction_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, records_with_timestamp)
        
        conn.commit()
        logger.info(f"Saved {len(records)} cumulative attendance records")
        
    except sqlite3.Error as e:
        logger.error(f"Error saving cumulative attendance: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def save_daily_attendance(records: List[Tuple]):
    """
    Save daily attendance records.
    
    Args:
        records: List of tuples (date, subject_code, subject_name, 
                 daily_present, daily_total, cumulative_present, cumulative_total)
    """
    if not records:
        logger.warning("No daily records to save")
        return
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.executemany("""
            INSERT OR REPLACE INTO daily_attendance 
            (date, subject_code, subject_name, daily_present, daily_total, 
             cumulative_present, cumulative_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, records)
        
        conn.commit()
        logger.info(f"Saved {len(records)} daily attendance records")
        
    except sqlite3.Error as e:
        logger.error(f"Error saving daily attendance: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def get_previous_day_attendance(subject_code: str, current_date: str) -> Optional[Tuple[int, int]]:
    """
    Get the most recent attendance record before the given date for a subject.
    
    Args:
        subject_code: Subject code to query
        current_date: Current date in YYYY-MM-DD format
    
    Returns:
        Tuple of (cumulative_present, cumulative_total) or None if not found
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT cumulative_present, cumulative_total
            FROM cumulative_attendance
            WHERE subject_code = ? AND date < ?
            ORDER BY date DESC
            LIMIT 1
        """, (subject_code, current_date))
        
        row = cur.fetchone()
        if row:
            return (row['cumulative_present'], row['cumulative_total'])
        return None
        
    except sqlite3.Error as e:
        logger.error(f"Error getting previous day attendance: {e}")
        raise
    finally:
        conn.close()


def get_yesterday_data() -> Dict[str, Tuple[int, int]]:
    """
    Get yesterday's cumulative attendance for all subjects.
    Compatible with old code.
    
    Returns:
        Dictionary mapping subject_code to (present, total)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT subject_code, cumulative_present, cumulative_total
            FROM cumulative_attendance
            WHERE date = (
                SELECT MAX(date) FROM cumulative_attendance WHERE date < DATE('now')
            )
        """)
        
        rows = cur.fetchall()
        return {row['subject_code']: (row['cumulative_present'], row['cumulative_total']) 
                for row in rows}
        
    except sqlite3.Error as e:
        logger.error(f"Error getting yesterday's data: {e}")
        return {}
    finally:
        conn.close()


def get_attendance_by_date_range(start_date: str, end_date: str, subject_code: str = None):
    """
    Get attendance records for a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        subject_code: Optional subject code filter
    
    Returns:
        List of attendance records
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        if subject_code:
            cur.execute("""
                SELECT * FROM daily_attendance
                WHERE date BETWEEN ? AND ? AND subject_code = ?
                ORDER BY date
            """, (start_date, end_date, subject_code))
        else:
            cur.execute("""
                SELECT * FROM daily_attendance
                WHERE date BETWEEN ? AND ?
                ORDER BY date, subject_code
            """, (start_date, end_date))
        
        return cur.fetchall()
        
    except sqlite3.Error as e:
        logger.error(f"Error getting attendance by date range: {e}")
        raise
    finally:
        conn.close()


def get_subject_history(subject_code: str):
    """
    Get all attendance records for a specific subject.
    
    Args:
        subject_code: Subject code to query
    
    Returns:
        List of attendance records ordered by date
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM daily_attendance
            WHERE subject_code = ?
            ORDER BY date
        """, (subject_code,))
        
        return cur.fetchall()
        
    except sqlite3.Error as e:
        logger.error(f"Error getting subject history: {e}")
        raise
    finally:
        conn.close()


def get_all_subjects() -> List[str]:
    """
    Get list of all unique subject codes in the database.
    
    Returns:
        List of subject codes
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT DISTINCT subject_code 
            FROM cumulative_attendance
            ORDER BY subject_code
        """)
        
        return [row['subject_code'] for row in cur.fetchall()]
        
    except sqlite3.Error as e:
        logger.error(f"Error getting all subjects: {e}")
        raise
    finally:
        conn.close()
