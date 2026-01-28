"""
Flask REST API for Attendance Tracker.

Provides endpoints for:
- Fetching latest attendance
- Getting subject history
- Triggering attendance scraper
- Overall statistics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import sys
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_postgres import (
    init_db,
    get_latest_attendance,
    get_subject_history,
    get_all_subjects
)
from attendance_calculator import (
    calculate_attendance_percentage,
    calculate_required_attendance,
    calculate_bunkable_classes
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Netlify frontend

# Initialize database on startup
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/attendance/latest', methods=['GET'])
def get_latest():
    """Get latest attendance for all subjects."""
    try:
        attendance_data = get_latest_attendance()
        
        # Add insights for each subject
        for subject in attendance_data:
            present = subject['present']
            total = subject['total']
            percentage = subject['percentage']
            
            if percentage < 75:
                subject['required'] = calculate_required_attendance(present, total, 75.0)
                subject['status'] = 'warning'
            else:
                subject['bunkable'] = calculate_bunkable_classes(present, total, 75.0)
                subject['status'] = 'good'
        
        return jsonify({
            'success': True,
            'data': attendance_data,
            'count': len(attendance_data)
        })
    
    except Exception as e:
        logger.error(f"Error fetching latest attendance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/attendance/history/<subject_code>', methods=['GET'])
def get_history(subject_code):
    """Get attendance history for a specific subject."""
    try:
        history = get_subject_history(subject_code)
        
        if not history:
            return jsonify({
                'success': False,
                'error': 'Subject not found'
            }), 404
        
        return jsonify({
            'success': True,
            'subject_code': subject_code,
            'data': history,
            'count': len(history)
        })
    
    except Exception as e:
        logger.error(f"Error fetching subject history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get list of all subjects."""
    try:
        subjects = get_all_subjects()
        
        return jsonify({
            'success': True,
            'data': subjects,
            'count': len(subjects)
        })
    
    except Exception as e:
        logger.error(f"Error fetching subjects: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall attendance statistics."""
    try:
        attendance_data = get_latest_attendance()
        
        if not attendance_data:
            return jsonify({
                'success': False,
                'error': 'No attendance data available'
            }), 404
        
        total_present = sum(s['present'] for s in attendance_data)
        total_classes = sum(s['total'] for s in attendance_data)
        overall_percentage = round((total_present / total_classes * 100) if total_classes > 0 else 0, 2)
        
        below_75 = [s for s in attendance_data if s['percentage'] < 75]
        above_75 = [s for s in attendance_data if s['percentage'] >= 75]
        
        return jsonify({
            'success': True,
            'data': {
                'overall_percentage': overall_percentage,
                'total_present': total_present,
                'total_classes': total_classes,
                'total_subjects': len(attendance_data),
                'subjects_below_75': len(below_75),
                'subjects_above_75': len(above_75),
                'latest_date': attendance_data[0]['date'] if attendance_data else None
            }
        })
    
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fetch', methods=['POST'])
def trigger_fetch():
    """
    Trigger attendance fetch.
    This will be implemented to run the scraper asynchronously.
    """
    try:
        # Import scraper module
        from scraper import run_scraper
        
        # Run scraper (this should be async in production)
        result = run_scraper()
        
        return jsonify({
            'success': True,
            'message': 'Attendance fetch completed',
            'data': result
        })
    
    except Exception as e:
        logger.error(f"Error triggering fetch: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
