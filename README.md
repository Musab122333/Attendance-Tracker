# Attendance Tracker - Cloud Web App

A modern, mobile-responsive web application for tracking student attendance from college portal. Deployed on the cloud with Netlify (frontend) and Render (backend).

## 🌟 Features

✅ **Beautiful Mobile UI** - Dark mode with vibrant gradients and smooth animations  
✅ **Cloud Deployed** - Access from anywhere via Netlify  
✅ **Real-time Data** - Fetch latest attendance with one click  
✅ **Smart Insights** - See required/bunkable classes to maintain 75%  
✅ **PostgreSQL Database** - Cloud-ready database on Render  
✅ **REST API** - Flask backend with comprehensive endpoints  

## 🚀 Live Demo

- **Frontend**: Your Netlify URL
- **Backend API**: https://attendance-api-cmr6.onrender.com

## 📱 Features

### Dashboard
- Overall attendance percentage
- Subject-wise breakdown
- Color-coded status indicators
- Required/bunkable classes insights

### Smart Calculations
- Attendance percentage tracking
- Classes needed to reach 75%
- Classes you can skip while maintaining 75%
- Daily attendance changes

### Mobile Optimized
- Responsive design
- Touch-friendly interface
- Fast loading
- Works on all devices

## 🏗️ Architecture

**Frontend (Netlify)**
- Static HTML/CSS/JavaScript
- Mobile-first responsive design
- Real-time API integration

**Backend (Render)**
- Flask REST API
- Selenium web scraper
- PostgreSQL database
- Automatic deployments

## 📂 Project Structure

```
attendance_bot/
├── api/
│   ├── app.py              # Flask REST API
│   ├── scraper.py          # Selenium scraper
│   └── requirements.txt    # Backend dependencies
├── public/
│   ├── index.html          # Dashboard
│   ├── css/style.css       # Styling
│   └── js/
│       ├── app.js          # Frontend logic
│       └── config.js       # API configuration
├── database_postgres.py    # PostgreSQL adapter
├── database_new.py         # SQLite adapter (local)
├── fetch_attendance_new.py # Local scraper script
├── subjects.py             # Subject mappings
├── utils.py                # Helper functions
├── Procfile               # Render config
├── netlify.toml           # Netlify config
└── DEPLOYMENT_GUIDE.md    # Deployment instructions
```

## 🔧 Local Development

### Prerequisites
- Python 3.11+
- Chrome browser
- PostgreSQL (optional, for local testing)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Musab122333/Attendance-Tracker.git
cd Attendance-Tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
$env:DATABASE_URL="your_postgres_url"
$env:PORTAL_USERNAME="your_username"
$env:PORTAL_PASSWORD="your_password"
```

4. Run the scraper locally:
```bash
python fetch_attendance_new.py
```

## 🌐 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

### Quick Deploy

**Backend (Render)**
1. Connect GitHub repository
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically

**Frontend (Netlify)**
1. Connect GitHub repository
2. Set publish directory to `public`
3. Update API URL in `public/js/config.js`
4. Deploy

## 🔑 Environment Variables

Required for backend deployment:

```
DATABASE_URL=postgresql://user:pass@host:port/db
PORTAL_USERNAME=your_college_username
PORTAL_PASSWORD=your_college_password
FLASK_ENV=production
```

## 📊 API Endpoints

- `GET /api/health` - Health check
- `GET /api/attendance/latest` - Latest attendance
- `GET /api/attendance/history/<code>` - Subject history
- `GET /api/subjects` - All subjects
- `GET /api/stats` - Overall statistics
- `POST /api/fetch` - Trigger scraper

## 🎨 Tech Stack

**Frontend**
- HTML5, CSS3, JavaScript
- Responsive design
- Fetch API

**Backend**
- Python 3.11
- Flask
- Selenium
- PostgreSQL
- BeautifulSoup4

**Deployment**
- Netlify (Frontend)
- Render (Backend + Database)

## 📝 Configuration

Update subject mappings in `subjects.py`:

```python
SUBJECT_MAP = {
    "22PC1CS302": "Data Structures",
    "22PE1DS302": "Machine Learning",
    # Add more subjects...
}
```

## 🔒 Security

- Credentials stored as environment variables
- `.env` file in `.gitignore`
- CORS configured for frontend
- Secure database connections

## 📈 Future Enhancements

- [ ] Email notifications for low attendance
- [ ] Attendance predictions
- [ ] Export to CSV/Excel
- [ ] Multiple user support
- [ ] Attendance trends and charts

## 🤝 Contributing

Feel free to fork and submit pull requests!

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

- VNR VJIET for the attendance portal
- Render for cloud hosting
- Netlify for frontend hosting

---

**Made with ❤️ for students**
