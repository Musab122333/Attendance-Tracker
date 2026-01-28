# Attendance Tracking System

A robust Python-based system for tracking student attendance from a college portal. The system parses HTML data, stores cumulative attendance in a SQLite database, and automatically calculates daily attendance changes.

## Features

✅ **Automated Data Extraction** - Selenium-based web scraping from college portal  
✅ **Robust HTML Parsing** - BeautifulSoup parser with error handling  
✅ **Dual Storage System** - Separate tables for cumulative and daily attendance  
✅ **Daily Calculation** - Automatic computation of daily attendance differences  
✅ **Historical Tracking** - Maintains complete attendance history  
✅ **Smart Insights** - Calculates required/bunkable classes to maintain target percentage  
✅ **Comprehensive Queries** - Pre-built analysis functions for trends and statistics  
✅ **Error Handling** - Graceful handling of malformed data and edge cases  

## Database Schema

### Cumulative Attendance Table
Stores raw cumulative attendance data from the portal.

```sql
CREATE TABLE cumulative_attendance (
    date TEXT NOT NULL,
    subject_code TEXT NOT NULL,
    subject_name TEXT NOT NULL,
    cumulative_present INTEGER NOT NULL,
    cumulative_total INTEGER NOT NULL,
    extraction_timestamp TEXT NOT NULL,
    PRIMARY KEY (date, subject_code)
);
```

### Daily Attendance Table
Stores calculated daily attendance changes.

```sql
CREATE TABLE daily_attendance (
    date TEXT NOT NULL,
    subject_code TEXT NOT NULL,
    subject_name TEXT NOT NULL,
    daily_present INTEGER,      -- NULL for first run
    daily_total INTEGER,         -- NULL for first run
    cumulative_present INTEGER NOT NULL,
    cumulative_total INTEGER NOT NULL,
    PRIMARY KEY (date, subject_code)
);
```

## Installation

1. **Clone the repository**
```bash
cd d:\attendance_bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install BeautifulSoup** (if not already installed)
```bash
pip install beautifulsoup4
```

## Usage

### First Time Setup

If you have existing data in the old schema, run the migration script:

```bash
python migrate_database.py
```

This will:
- Backup your existing database
- Migrate data to the new schema
- Calculate historical daily attendance
- Validate the migration

### Daily Attendance Fetching

Run the main script to fetch today's attendance:

```bash
python fetch_attendance_new.py
```

This will:
1. Log into the college portal
2. Extract attendance HTML
3. Parse and validate data
4. Save cumulative attendance
5. Calculate and save daily attendance
6. Display summary with insights

### Analyzing Attendance Data

Run the query examples to analyze your attendance:

```bash
python query_examples.py
```

This displays:
- Latest attendance for all subjects
- Overall statistics
- Subjects below 75% threshold
- Weekly attendance summary

## Module Overview

### Core Modules

| Module | Purpose |
|--------|---------|
| `database_new.py` | Enhanced database operations with proper schema |
| `html_parser.py` | Robust HTML parsing with BeautifulSoup |
| `attendance_calculator.py` | Daily attendance calculation and insights |
| `utils.py` | Logging, validation, and helper functions |
| `fetch_attendance_new.py` | Main orchestration script |
| `query_examples.py` | Pre-built analysis queries |

### Legacy Files

| File | Status |
|------|--------|
| `database.py` | Old database module (deprecated) |
| `fetch_attendance.py` | Old fetch script (deprecated) |

## Configuration

Edit credentials in `fetch_attendance_new.py`:

```python
USERNAME = "your_username"
PASSWORD = "your_password"
```

Update subject mappings in `subjects.py`:

```python
SUBJECT_MAP = {
    "22PC1CS302": "Data Structures",
    "22PE1DS302": "Machine Learning",
    # Add more subjects...
}
```

## Daily Attendance Calculation

The system calculates daily attendance using:

```
today_present = today_cumulative_present - yesterday_cumulative_present
today_total = today_cumulative_total - yesterday_cumulative_total
```

**Special Cases:**
- **First Run**: Daily values are `NULL` (no previous data)
- **New Subject**: Daily values are `NULL` for first occurrence
- **Negative Values**: Logged as warning (indicates data correction)

## Example Queries

### Get Latest Attendance
```python
from query_examples import print_latest_attendance
print_latest_attendance()
```

### Get Subject History
```python
from database_new import get_subject_history
history = get_subject_history("22PC1CS302")
for record in history:
    print(record)
```

### Get Attendance Trend
```python
from query_examples import get_attendance_trend
trend = get_attendance_trend("22PC1CS302", days=7)
```

### Find Subjects Below Threshold
```python
from query_examples import print_subjects_below_threshold
print_subjects_below_threshold(75.0)
```

## Insights and Calculations

The system provides smart insights:

### Required Classes
Calculates how many consecutive classes you need to attend to reach 75%:

```python
from attendance_calculator import calculate_required_attendance
required = calculate_required_attendance(present=45, total=60, target=75.0)
print(f"Need to attend {required} consecutive classes")
```

### Bunkable Classes
Calculates how many classes you can skip while maintaining 75%:

```python
from attendance_calculator import calculate_bunkable_classes
bunkable = calculate_bunkable_classes(present=50, total=60, target=75.0)
print(f"Can skip {bunkable} classes")
```

## Automation

To run the script daily automatically:

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily
4. Action: Start a program
5. Program: `python`
6. Arguments: `d:\attendance_bot\fetch_attendance_new.py`
7. Start in: `d:\attendance_bot`

### Linux/Mac Cron
```bash
# Run daily at 8 PM
0 20 * * * cd /path/to/attendance_bot && python fetch_attendance_new.py
```

## Error Handling

The system handles:
- ✅ Missing or malformed HTML elements
- ✅ Invalid numeric values
- ✅ Duplicate records (uses UPSERT)
- ✅ Database transaction failures
- ✅ Missing previous day data
- ✅ Login failures

All errors are logged to `attendance.log`.

## Database Maintenance

### View Database
```bash
sqlite3 attendance.db
```

### Common Queries
```sql
-- Check for duplicates
SELECT date, subject_code, COUNT(*) 
FROM cumulative_attendance 
GROUP BY date, subject_code 
HAVING COUNT(*) > 1;

-- View latest records
SELECT * FROM daily_attendance 
ORDER BY date DESC LIMIT 10;

-- Calculate overall percentage
SELECT 
    SUM(cumulative_present) as total_present,
    SUM(cumulative_total) as total_classes,
    (SUM(cumulative_present) * 100.0 / SUM(cumulative_total)) as percentage
FROM daily_attendance
WHERE date = (SELECT MAX(date) FROM daily_attendance);
```

## Troubleshooting

### HTML Parsing Fails
- Check `debug_modal.html` for the actual HTML structure
- Update parser in `html_parser.py` if portal structure changed

### Login Issues
- Verify credentials in `fetch_attendance_new.py`
- Check if portal URL has changed
- Increase wait times if portal is slow

### Database Locked
- Close any open SQLite connections
- Restart the script

### Migration Issues
- Restore from backup: `copy attendance_backup_*.db attendance.db`
- Check logs in `attendance.log`

## Contributing

Feel free to enhance the system with:
- Additional analysis queries
- Better visualization
- Export to CSV/Excel
- Email notifications
- Dashboard UI

## License

This project is for educational purposes.

## Support

For issues or questions, check the logs in `attendance.log` or review the implementation plan in the brain artifacts directory.
