"""
Example queries for analyzing attendance data.

This module demonstrates common queries for:
- Daily attendance trends
- Subject-wise analysis
- Attendance percentage calculations
- Historical data retrieval
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from database_new import get_connection, get_subject_history, get_all_subjects
from attendance_calculator import calculate_attendance_percentage

logger = logging.getLogger(__name__)


def get_latest_attendance():
    """Get the most recent attendance record for all subjects."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                date,
                subject_code,
                subject_name,
                daily_present,
                daily_total,
                cumulative_present,
                cumulative_total
            FROM daily_attendance
            WHERE date = (SELECT MAX(date) FROM daily_attendance)
            ORDER BY subject_code
        """)
        
        return cur.fetchall()
    finally:
        conn.close()


def get_attendance_trend(subject_code, days=7):
    """
    Get attendance trend for a subject over the last N days.
    
    Args:
        subject_code: Subject code to query
        days: Number of days to look back
    
    Returns:
        List of attendance records
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                date,
                daily_present,
                daily_total,
                cumulative_present,
                cumulative_total
            FROM daily_attendance
            WHERE subject_code = ?
            AND date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        """, (subject_code, days))
        
        return cur.fetchall()
    finally:
        conn.close()


def get_overall_statistics():
    """Get overall attendance statistics across all subjects."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get latest cumulative data for each subject
        cur.execute("""
            SELECT 
                subject_code,
                subject_name,
                cumulative_present,
                cumulative_total
            FROM daily_attendance
            WHERE date = (SELECT MAX(date) FROM daily_attendance)
        """)
        
        records = cur.fetchall()
        
        total_present = sum(r['cumulative_present'] for r in records)
        total_classes = sum(r['cumulative_total'] for r in records)
        
        return {
            'total_present': total_present,
            'total_classes': total_classes,
            'overall_percentage': calculate_attendance_percentage(total_present, total_classes),
            'subjects_count': len(records),
            'subjects': records
        }
    finally:
        conn.close()


def get_subjects_below_threshold(threshold=75.0):
    """
    Get subjects with attendance below a threshold.
    
    Args:
        threshold: Minimum attendance percentage
    
    Returns:
        List of subjects below threshold
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                subject_code,
                subject_name,
                cumulative_present,
                cumulative_total,
                (cumulative_present * 100.0 / cumulative_total) as percentage
            FROM daily_attendance
            WHERE date = (SELECT MAX(date) FROM daily_attendance)
            AND (cumulative_present * 100.0 / cumulative_total) < ?
            ORDER BY percentage ASC
        """, (threshold,))
        
        return cur.fetchall()
    finally:
        conn.close()


def get_weekly_summary():
    """Get weekly attendance summary."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                subject_code,
                subject_name,
                SUM(COALESCE(daily_present, 0)) as week_present,
                SUM(COALESCE(daily_total, 0)) as week_total
            FROM daily_attendance
            WHERE date >= date('now', '-7 days')
            GROUP BY subject_code, subject_name
            HAVING week_total > 0
            ORDER BY subject_code
        """)
        
        return cur.fetchall()
    finally:
        conn.close()


def get_date_range_summary(start_date, end_date):
    """
    Get attendance summary for a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Summary statistics
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                subject_code,
                subject_name,
                SUM(COALESCE(daily_present, 0)) as period_present,
                SUM(COALESCE(daily_total, 0)) as period_total,
                COUNT(*) as days_recorded
            FROM daily_attendance
            WHERE date BETWEEN ? AND ?
            GROUP BY subject_code, subject_name
            ORDER BY subject_code
        """, (start_date, end_date))
        
        return cur.fetchall()
    finally:
        conn.close()


def print_latest_attendance():
    """Print the latest attendance in a formatted way."""
    records = get_latest_attendance()
    
    if not records:
        print("No attendance records found.")
        return
    
    print("\n" + "="*80)
    print(f"📅 LATEST ATTENDANCE - {records[0]['date']}")
    print("="*80)
    
    for record in records:
        subject_name = record['subject_name']
        cum_present = record['cumulative_present']
        cum_total = record['cumulative_total']
        daily_present = record['daily_present']
        daily_total = record['daily_total']
        
        percentage = calculate_attendance_percentage(cum_present, cum_total)
        
        print(f"\n{subject_name}")
        print(f"  Cumulative: {cum_present}/{cum_total} ({percentage:.1f}%)")
        
        if daily_present is not None and daily_total is not None:
            if daily_total > 0:
                daily_pct = calculate_attendance_percentage(daily_present, daily_total)
                print(f"  Today: +{daily_present}/{daily_total} ({daily_pct:.1f}%)")
            else:
                print(f"  Today: No classes")
        else:
            print(f"  Today: First record")
    
    print("\n" + "="*80)


def print_overall_statistics():
    """Print overall statistics."""
    stats = get_overall_statistics()
    
    print("\n" + "="*80)
    print("📊 OVERALL STATISTICS")
    print("="*80)
    print(f"\nTotal Classes Attended: {stats['total_present']}/{stats['total_classes']}")
    print(f"Overall Percentage: {stats['overall_percentage']:.2f}%")
    print(f"Number of Subjects: {stats['subjects_count']}")
    print("="*80)


def print_subjects_below_threshold(threshold=75.0):
    """Print subjects below attendance threshold."""
    subjects = get_subjects_below_threshold(threshold)
    
    print("\n" + "="*80)
    print(f"⚠️  SUBJECTS BELOW {threshold}% ATTENDANCE")
    print("="*80)
    
    if not subjects:
        print(f"\n✅ All subjects are above {threshold}% attendance!")
    else:
        for subject in subjects:
            print(f"\n{subject['subject_name']}")
            print(f"  Attendance: {subject['cumulative_present']}/{subject['cumulative_total']}")
            print(f"  Percentage: {subject['percentage']:.1f}%")
    
    print("="*80)


def print_weekly_summary():
    """Print weekly attendance summary."""
    records = get_weekly_summary()
    
    print("\n" + "="*80)
    print("📅 WEEKLY ATTENDANCE SUMMARY (Last 7 Days)")
    print("="*80)
    
    if not records:
        print("\nNo attendance records for the past week.")
    else:
        for record in records:
            week_present = record['week_present']
            week_total = record['week_total']
            
            if week_total > 0:
                week_pct = calculate_attendance_percentage(week_present, week_total)
                print(f"\n{record['subject_name']}")
                print(f"  This Week: {week_present}/{week_total} ({week_pct:.1f}%)")
    
    print("="*80)


# Example usage
if __name__ == "__main__":
    from utils import setup_logging
    setup_logging()
    
    print("\n🔍 ATTENDANCE ANALYSIS\n")
    
    # Print latest attendance
    print_latest_attendance()
    
    # Print overall statistics
    print_overall_statistics()
    
    # Print subjects below threshold
    print_subjects_below_threshold(75.0)
    
    # Print weekly summary
    print_weekly_summary()
