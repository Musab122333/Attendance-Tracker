"""
PostgreSQL database adapter for cloud deployment.

This module provides the same interface as database_new.py but uses PostgreSQL
instead of SQLite for cloud compatibility (Render/Railway/Netlify).
"""

import psycopg2
from psycopg2 import pool
import logging
import os
from typing import List, Tuple, Optional, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database connection pool
connection_pool = None


def init_connection_pool():
    """Initialize PostgreSQL connection pool."""
    global connection_pool
    
    if connection_pool is None:
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        try:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,  # min and max connections
                database_url
            )
            logger.info("PostgreSQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise


@contextmanager
def get_connection():
    """Get database connection from pool with context manager."""
    if connection_pool is None:
        init_connection_pool()
    
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)


def init_db():
    """
    Initialize database with enhanced schema.
    Creates tables with proper constraints and indexes.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            # Create cumulative_attendance table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cumulative_attendance (
                    date DATE NOT NULL,
                    subject_code VARCHAR(50) NOT NULL,
                    subject_name VARCHAR(200) NOT NULL,
                    cumulative_present INTEGER NOT NULL,
                    cumulative_total INTEGER NOT NULL,
                    extraction_timestamp TIMESTAMP NOT NULL,
                    PRIMARY KEY (date, subject_code)
                )
            """)
            
            # Create indexes for cumulative_attendance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_cumulative_date 
                ON cumulative_attendance(date DESC)
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_cumulative_subject 
                ON cumulative_attendance(subject_code)
            """)
            
            # Create daily_attendance table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS daily_attendance (
                    date DATE NOT NULL,
                    subject_code VARCHAR(50) NOT NULL,
                    subject_name VARCHAR(200) NOT NULL,
                    daily_present INTEGER,
                    daily_total INTEGER,
                    cumulative_present INTEGER NOT NULL,
                    cumulative_total INTEGER NOT NULL,
                    PRIMARY KEY (date, subject_code)
                )
            """)
            
            # Create indexes for daily_attendance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_daily_date 
                ON daily_attendance(date DESC)
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_daily_subject 
                ON daily_attendance(subject_code)
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to initialize database: {e}")
            raise


def save_cumulative_attendance(records: List[Tuple], extraction_timestamp: str = None):
    """
    Save cumulative attendance records.
    Uses INSERT ON CONFLICT to handle duplicates gracefully.
    
    Args:
        records: List of tuples (date, subject_code, subject_name, present, total)
        extraction_timestamp: Timestamp of extraction (defaults to current time)
    """
    if not records:
        logger.warning("No records to save")
        return
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            # Use NOW() if no timestamp provided
            if extraction_timestamp is None:
                extraction_timestamp = 'NOW()'
                data = [
                    (date, code, name, present, total)
                    for date, code, name, present, total in records
                ]
                
                cur.executemany("""
                    INSERT INTO cumulative_attendance 
                    (date, subject_code, subject_name, cumulative_present, cumulative_total, extraction_timestamp)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (date, subject_code) 
                    DO UPDATE SET
                        subject_name = EXCLUDED.subject_name,
                        cumulative_present = EXCLUDED.cumulative_present,
                        cumulative_total = EXCLUDED.cumulative_total,
                        extraction_timestamp = EXCLUDED.extraction_timestamp
                """, data)
            else:
                data = [
                    (date, code, name, present, total, extraction_timestamp)
                    for date, code, name, present, total in records
                ]
                
                cur.executemany("""
                    INSERT INTO cumulative_attendance 
                    (date, subject_code, subject_name, cumulative_present, cumulative_total, extraction_timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (date, subject_code) 
                    DO UPDATE SET
                        subject_name = EXCLUDED.subject_name,
                        cumulative_present = EXCLUDED.cumulative_present,
                        cumulative_total = EXCLUDED.cumulative_total,
                        extraction_timestamp = EXCLUDED.extraction_timestamp
                """, data)
            
            conn.commit()
            logger.info(f"Saved {len(records)} cumulative attendance records")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save cumulative attendance: {e}")
            raise


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
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.executemany("""
                INSERT INTO daily_attendance 
                (date, subject_code, subject_name, daily_present, daily_total, 
                 cumulative_present, cumulative_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, subject_code) 
                DO UPDATE SET
                    subject_name = EXCLUDED.subject_name,
                    daily_present = EXCLUDED.daily_present,
                    daily_total = EXCLUDED.daily_total,
                    cumulative_present = EXCLUDED.cumulative_present,
                    cumulative_total = EXCLUDED.cumulative_total
            """, records)
            
            conn.commit()
            logger.info(f"Saved {len(records)} daily attendance records")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save daily attendance: {e}")
            raise


def get_previous_day_attendance(subject_code: str, current_date: str) -> Optional[Tuple[int, int]]:
    """
    Get the most recent attendance record before the given date for a subject.
    
    Args:
        subject_code: Subject code to query
        current_date: Current date in YYYY-MM-DD format
    
    Returns:
        Tuple of (cumulative_present, cumulative_total) or None if not found
    """
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT cumulative_present, cumulative_total
                FROM cumulative_attendance
                WHERE subject_code = %s AND date < %s
                ORDER BY date DESC
                LIMIT 1
            """, (subject_code, current_date))
            
            result = cur.fetchone()
            return result if result else None
            
        except Exception as e:
            logger.error(f"Failed to get previous day attendance: {e}")
            return None


def get_yesterday_data() -> Dict[str, Tuple[int, int]]:
    """
    Get yesterday's cumulative attendance for all subjects.
    Compatible with old code.
    
    Returns:
        Dictionary mapping subject_code to (present, total)
    """
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT subject_code, cumulative_present, cumulative_total
                FROM cumulative_attendance
                WHERE date = (
                    SELECT MAX(date) FROM cumulative_attendance WHERE date < CURRENT_DATE
                )
            """)
            
            rows = cur.fetchall()
            return {row[0]: (row[1], row[2]) for row in rows}
            
        except Exception as e:
            logger.error(f"Failed to get yesterday's data: {e}")
            return {}


def get_latest_attendance() -> List[Dict]:
    """
    Get latest attendance for all subjects.
    
    Returns:
        List of dictionaries with attendance data
    """
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT 
                    subject_code,
                    subject_name,
                    cumulative_present,
                    cumulative_total,
                    date
                FROM daily_attendance
                WHERE date = (SELECT MAX(date) FROM daily_attendance)
                ORDER BY subject_code
            """)
            
            rows = cur.fetchall()
            return [
                {
                    'subject_code': row[0],
                    'subject_name': row[1],
                    'present': row[2],
                    'total': row[3],
                    'date': str(row[4]),
                    'percentage': round((row[2] / row[3] * 100) if row[3] > 0 else 0, 2)
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get latest attendance: {e}")
            return []


def get_subject_history(subject_code: str) -> List[Dict]:
    """
    Get all attendance records for a specific subject.
    
    Args:
        subject_code: Subject code to query
    
    Returns:
        List of attendance records ordered by date
    """
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT 
                    date,
                    subject_name,
                    daily_present,
                    daily_total,
                    cumulative_present,
                    cumulative_total
                FROM daily_attendance
                WHERE subject_code = %s
                ORDER BY date ASC
            """, (subject_code,))
            
            rows = cur.fetchall()
            return [
                {
                    'date': str(row[0]),
                    'subject_name': row[1],
                    'daily_present': row[2],
                    'daily_total': row[3],
                    'cumulative_present': row[4],
                    'cumulative_total': row[5],
                    'percentage': round((row[4] / row[5] * 100) if row[5] > 0 else 0, 2)
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get subject history: {e}")
            return []


def get_all_subjects() -> List[str]:
    """
    Get list of all unique subject codes in the database.
    
    Returns:
        List of subject codes
    """
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT DISTINCT subject_code
                FROM daily_attendance
                ORDER BY subject_code
            """)
            
            rows = cur.fetchall()
            return [row[0] for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get all subjects: {e}")
            return []
