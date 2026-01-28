# Deployment Guide - Attendance Tracker Web App

Complete guide to deploy your attendance tracker to the cloud with Railway/Render (backend) and Netlify (frontend).

## Architecture

- **Frontend**: Static HTML/CSS/JS hosted on Netlify
- **Backend**: Flask API with Selenium on Railway or Render
- **Database**: PostgreSQL (provided by Railway/Render)

---

## Part 1: Deploy Backend to Railway (Recommended) or Render

### Option A: Railway Deployment

#### 1. Create Railway Account
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

#### 2. Create New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Connect your `Attendance-Tracker` repository

#### 3. Add PostgreSQL Database
- In your project, click "New"
- Select "Database" → "PostgreSQL"
- Railway will automatically create a database and provide `DATABASE_URL`

#### 4. Configure Environment Variables
Go to your service → Variables tab and add:
```
DATABASE_URL=(automatically provided by Railway)
PORTAL_USERNAME=23071A6740
PORTAL_PASSWORD=Musab@VNR99
FLASK_ENV=production
```

#### 5. Configure Build Settings
- Root Directory: `/`
- Build Command: `pip install -r api/requirements.txt`
- Start Command: `gunicorn api.app:app`

#### 6. Deploy
- Railway will automatically deploy
- Note your deployment URL: `https://your-app.railway.app`

---

### Option B: Render Deployment

#### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub

#### 2. Create PostgreSQL Database
- Click "New +" → "PostgreSQL"
- Name: `attendance-db`
- Note the Internal Database URL

#### 3. Create Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Configure:
  - **Name**: `attendance-api`
  - **Environment**: `Python 3`
  - **Build Command**: `pip install -r api/requirements.txt`
  - **Start Command**: `gunicorn api.app:app`

#### 4. Add Environment Variables
```
DATABASE_URL=(paste your PostgreSQL Internal Database URL)
PORTAL_USERNAME=23071A6740
PORTAL_PASSWORD=Musab@VNR99
FLASK_ENV=production
PORT=10000
```

#### 5. Deploy
- Click "Create Web Service"
- Wait for deployment to complete
- Note your URL: `https://your-app.onrender.com`

---

## Part 2: Deploy Frontend to Netlify

#### 1. Create Netlify Account
- Go to [netlify.com](https://netlify.com)
- Sign up with GitHub

#### 2. Update API URL
Before deploying, update `public/js/config.js`:
```javascript
const API_URL = 'https://your-app.railway.app';  // or your Render URL
```

Commit and push this change:
```bash
git add public/js/config.js
git commit -m "Update API URL for production"
git push origin main
```

#### 3. Create New Site
- Click "Add new site" → "Import an existing project"
- Choose GitHub and select your repository
- Configure:
  - **Branch**: `main`
  - **Base directory**: (leave empty)
  - **Build command**: (leave empty)
  - **Publish directory**: `public`

#### 4. Deploy
- Click "Deploy site"
- Netlify will assign you a URL like `https://random-name.netlify.app`
- You can customize this in Site settings → Domain management

---

## Part 3: Initialize Database

After both deployments are complete:

### Option 1: Use API Endpoint
Visit your backend URL in browser:
```
https://your-app.railway.app/api/health
```

This will automatically initialize the database tables.

### Option 2: Run Migration Script
If you have existing SQLite data, you can migrate it:

1. Install PostgreSQL locally
2. Get your DATABASE_URL from Railway/Render
3. Set it as environment variable:
```bash
$env:DATABASE_URL="your_database_url"
```
4. Run migration (you'll need to create a migration script)

---

## Part 4: Test Your Deployment

### 1. Test Backend API
Visit these endpoints:
- Health check: `https://your-app.railway.app/api/health`
- Latest attendance: `https://your-app.railway.app/api/attendance/latest`
- Stats: `https://your-app.railway.app/api/stats`

### 2. Test Frontend
- Open your Netlify URL: `https://your-app.netlify.app`
- You should see the dashboard
- Click "Fetch Latest" to trigger the scraper
- Verify data appears

### 3. Test from Mobile
- Open your Netlify URL on your mobile browser
- Everything should be fully responsive

---

## Troubleshooting

### Backend Issues

**Database Connection Error**
- Verify DATABASE_URL is set correctly
- Check PostgreSQL service is running
- Ensure database is accessible from your web service

**Selenium/Chrome Error**
- Railway/Render should auto-install Chrome
- Check logs for specific errors
- Verify webdriver-manager is in requirements.txt

**Import Errors**
- Ensure all parent modules are importable
- Check Python path configuration
- Verify all dependencies in requirements.txt

### Frontend Issues

**API Connection Error**
- Verify API_URL in config.js is correct
- Check CORS is enabled on backend
- Ensure backend is deployed and running

**Data Not Loading**
- Check browser console for errors
- Verify API endpoints are responding
- Check network tab in browser dev tools

---

## Monitoring & Maintenance

### Railway
- View logs: Project → Service → Logs
- Monitor usage: Project → Usage
- Free tier: $5/month credit

### Render
- View logs: Service → Logs
- Monitor usage: Account → Usage
- Free tier: 750 hours/month

### Netlify
- View deploys: Site → Deploys
- Monitor bandwidth: Site → Analytics
- Free tier: 100GB bandwidth/month

---

## Updating Your App

### Update Backend
```bash
git add .
git commit -m "Update backend"
git push origin main
```
Railway/Render will auto-deploy.

### Update Frontend
```bash
git add public/
git commit -m "Update frontend"
git push origin main
```
Netlify will auto-deploy.

---

## Security Notes

1. **Never commit .env file** - It's in .gitignore
2. **Use environment variables** for all secrets
3. **Keep credentials secure** in Railway/Render dashboard
4. **Monitor usage** to avoid unexpected charges
5. **Enable 2FA** on all cloud accounts

---

## Cost Estimates

**Free Tier Limits:**
- Railway: $5/month credit (enough for this app)
- Render: 750 hours/month (enough for this app)
- Netlify: 100GB bandwidth (more than enough)

**Estimated Monthly Cost: $0** (within free tiers)

---

## Support

If you encounter issues:
1. Check the logs on Railway/Render
2. Check browser console for frontend errors
3. Verify all environment variables are set
4. Ensure database is initialized

For Railway-specific issues: [railway.app/help](https://railway.app/help)
For Render-specific issues: [render.com/docs](https://render.com/docs)
For Netlify-specific issues: [docs.netlify.com](https://docs.netlify.com)
