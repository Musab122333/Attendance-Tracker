// Main application JavaScript

// Load attendance data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAttendance();
    loadStats();
});

// Load latest attendance data
async function loadAttendance() {
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const subjectsContainer = document.getElementById('subjectsContainer');

    loadingState.style.display = 'block';
    errorState.style.display = 'none';
    subjectsContainer.innerHTML = '';

    try {
        const response = await fetch(`${API_URL}/api/attendance/latest`);
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to fetch data');
        }

        loadingState.style.display = 'none';

        if (result.data.length === 0) {
            subjectsContainer.innerHTML = '<p class="no-data">No attendance data available. Click "Fetch Latest" to get started.</p>';
            return;
        }

        // Update last updated time
        if (result.data[0].date) {
            document.getElementById('lastUpdated').textContent = `Last updated: ${formatDate(result.data[0].date)}`;
        }

        // Render subject cards
        result.data.forEach(subject => {
            const card = createSubjectCard(subject);
            subjectsContainer.appendChild(card);
        });

    } catch (error) {
        console.error('Error loading attendance:', error);
        loadingState.style.display = 'none';
        errorState.style.display = 'block';
    }
}

// Load overall statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/api/stats`);
        const result = await response.json();

        if (result.success) {
            const stats = result.data;
            document.getElementById('overallPercentage').textContent = `${stats.overall_percentage}%`;
            document.getElementById('totalSubjects').textContent = stats.total_subjects;
            document.getElementById('belowTarget').textContent = stats.subjects_below_75;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Create subject card element
function createSubjectCard(subject) {
    const card = document.createElement('div');
    card.className = `subject-card ${getStatusClass(subject.percentage)}`;

    const percentage = subject.percentage;
    const statusIcon = percentage >= 75 ? '✅' : percentage >= 70 ? '⚠️' : '❌';

    let insightHTML = '';
    if (subject.status === 'warning' && subject.required) {
        insightHTML = `<div class="insight warning">Need ${subject.required} consecutive classes to reach 75%</div>`;
    } else if (subject.status === 'good' && subject.bunkable > 0) {
        insightHTML = `<div class="insight good">Can skip ${subject.bunkable} classes</div>`;
    }

    card.innerHTML = `
        <div class="card-header">
            <h3 class="subject-name">${subject.subject_name}</h3>
            <span class="status-icon">${statusIcon}</span>
        </div>
        <div class="card-body">
            <div class="attendance-stats">
                <div class="stat">
                    <span class="label">Present:</span>
                    <span class="value">${subject.present}</span>
                </div>
                <div class="stat">
                    <span class="label">Total:</span>
                    <span class="value">${subject.total}</span>
                </div>
            </div>
            <div class="percentage-bar">
                <div class="percentage-fill" style="width: ${percentage}%"></div>
            </div>
            <div class="percentage-text">${percentage}%</div>
            ${insightHTML}
        </div>
        <div class="card-footer">
            <button class="btn-link" onclick="viewHistory('${subject.subject_code}')">
                View History →
            </button>
        </div>
    `;

    return card;
}

// Get status class based on percentage
function getStatusClass(percentage) {
    if (percentage >= 75) return 'status-good';
    if (percentage >= 70) return 'status-warning';
    return 'status-danger';
}

// Trigger attendance fetch
async function fetchAttendance() {
    const fetchBtn = document.getElementById('fetchBtn');
    const fetchBtnText = document.getElementById('fetchBtnText');
    const fetchSpinner = document.getElementById('fetchSpinner');

    fetchBtn.disabled = true;
    fetchBtnText.style.display = 'none';
    fetchSpinner.style.display = 'inline-block';

    try {
        const response = await fetch(`${API_URL}/api/fetch`, {
            method: 'POST'
        });
        const result = await response.json();

        if (result.success) {
            // Reload attendance data
            await loadAttendance();
            await loadStats();
            showNotification('✅ Attendance fetched successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to fetch attendance');
        }

    } catch (error) {
        console.error('Error fetching attendance:', error);
        showNotification('❌ Failed to fetch attendance. Please try again.', 'error');
    } finally {
        fetchBtn.disabled = false;
        fetchBtnText.style.display = 'inline';
        fetchSpinner.style.display = 'none';
    }
}

// View subject history (placeholder - can be expanded)
function viewHistory(subjectCode) {
    // For now, just alert - can be expanded to show modal or navigate to detail page
    alert(`Viewing history for ${subjectCode}\n\nThis feature can be expanded to show detailed history charts.`);
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
