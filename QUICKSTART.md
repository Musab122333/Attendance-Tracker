# Quick Start Guide - Attendance Tracking System

## 🚀 How to Run

### Option 1: First Time Setup (If you have existing data)

If you already have data in the old `attendance.db`, migrate it first:

```bash
cd d:\attendance_bot
python migrate_database.py
```

This will backup your data and migrate it to the new schema.

---

### Option 2: Fresh Start (No existing data)

If this is your first time or you want to start fresh:

```bash
cd d:\attendance_bot
python fetch_attendance_new.py
```

The database will be created automatically on first run.

---

## 📊 Daily Usage

Run this command daily to fetch and track attendance:

```bash
python fetch_attendance_new.py
```

**What it does:**
1. ✅ Logs into the portal
2. ✅ Extracts attendance HTML
3. ✅ Parses and validates data
4. ✅ Saves cumulative attendance
5. ✅ Calculates daily changes
6. ✅ Shows insights (required/bunkable classes)

---

## 📈 View Analysis & Reports

After fetching attendance, analyze your data:

```bash
python query_examples.py
```

**Shows:**
- Latest attendance for all subjects
- Overall statistics
- Subjects below 75% threshold
- Weekly attendance summary

---

## 🔧 Troubleshooting

### If you get import errors:

```bash
pip install beautifulsoup4
```

### If migration fails:

Your data is backed up automatically. Check the backup file:
```
attendance_backup_YYYYMMDD_HHMMSS.db
```

### If you want to test the parser:

```bash
python -c "from html_parser import parse_attendance_auto; html = open('debug_modal.html', encoding='utf-8').read(); print(parse_attendance_auto(html))"
```

---

## 📁 File Structure

**New Files (Use these):**
- `fetch_attendance_new.py` - Main script ⭐
- `database_new.py` - Database operations
- `html_parser.py` - HTML parsing
- `attendance_calculator.py` - Calculations
- `utils.py` - Utilities
- `query_examples.py` - Analysis queries
- `migrate_database.py` - One-time migration

**Old Files (Deprecated):**
- `fetch_attendance.py` - Old script
- `database.py` - Old database module

---

## ⚙️ Configuration

Edit `fetch_attendance_new.py` to update credentials:

```python
USERNAME = "your_username"  # Line 41
PASSWORD = "your_password"  # Line 42
```

---

## 🎯 Quick Commands Reference

| Task | Command |
|------|---------|
| **Fetch today's attendance** | `python fetch_attendance_new.py` |
| **View analysis** | `python query_examples.py` |
| **Migrate old data** | `python migrate_database.py` |
| **Check database** | `sqlite3 attendance.db` |

---

## 💡 Example Output

When you run `fetch_attendance_new.py`, you'll see:

```
======================================================================
📅 ATTENDANCE SUMMARY - 2026-01-24
======================================================================

📊 Today's Cumulative Attendance:

  Data Structures
    Cumulative: 6/9 (66.7%)
    ⚠️  Need to attend 4 consecutive classes to reach 75%

  Machine Learning
    Cumulative: 11/13 (84.6%)
    ✅ Can skip 2 classes while maintaining 75%

📈 Today's Attendance Change:

  Data Structures: +1/2 (50.0%)
  Machine Learning: +1/1 (100.0%)
======================================================================
```

---

## 🔄 Automation (Optional)

To run automatically every day at 8 PM:

### Windows Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task → Daily
3. Program: `python`
4. Arguments: `d:\attendance_bot\fetch_attendance_new.py`
5. Start in: `d:\attendance_bot`

---

## ❓ Need Help?

Check the logs:
```
attendance.log
```

All errors and warnings are logged there.
