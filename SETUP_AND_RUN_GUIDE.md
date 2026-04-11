# 🌍 GeoSpatial Site Readiness Analyzer - Setup & Run Guide

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **npm** or **yarn** (package manager)

## 🚀 Quick Start (Recommended)

### Step 1: Clone/Navigate to Project Directory
```bash
```

### Step 2: Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** `http://localhost:8000`

### Step 3: Frontend Setup (New Terminal/Command Prompt)
```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install Node.js dependencies
npm install

# Start the frontend development server
npm run dev
```

**Frontend will be available at:** `http://localhost:3000`

## 🎯 How to Use the Application

### 1. Open Your Browser
Navigate to: `http://localhost:3000`

### 2. Interact with the Map
- **Click anywhere on the map** to analyze that location
- **Use the "Test API" button** to test with Ahmedabad center coordinates
- **View results** in the right panel showing:
  - Overall site readiness score (0-100)
  - Recommendation verdict
  - Detailed analysis breakdown

### 3. Understanding the Results
- **Score 70-100**: Highly recommended location
- **Score 50-69**: Good location with considerations
- **Score 0-49**: Challenging location, consider alternatives

## 🔧 Troubleshooting

### Backend Issues

**Problem: "Module not found" errors**
```bash
cd backend
pip install fastapi uvicorn sqlalchemy pydantic python-multipart
```

**Problem: Database connection issues**
- The app uses SQLite (no additional database setup required)
- Database file will be created automatically at `backend/geositedb.sqlite`

**Problem: Port 8000 already in use**
```bash
# Use a different port
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
# Then update frontend API calls to use port 8001
```

### Frontend Issues

**Problem: "npm command not found"**
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation

**Problem: Port 3000 already in use**
```bash
# The app will automatically suggest an alternative port
# Or manually specify a port in vite.config.ts
```

**Problem: Map not loading**
- Check browser console for errors (F12)
- Ensure internet connection (map tiles load from OpenStreetMap)
- Try refreshing the page

**Problem: API calls failing**
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify backend health at: `http://localhost:8000/health`

## 📊 API Testing

### Test Backend Directly
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test scoring endpoint
curl -X POST "http://localhost:8000/api/v1/enhanced/score" \
  -H "Content-Type: application/json" \
  -d '{"lat": 23.0225, "lng": 72.5714, "use_case": "retail"}'
```

### API Documentation
Visit: `http://localhost:8000/docs` for interactive API documentation

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── services/           # Business logic services
│   ├── api/               # API routes
│   └── core/              # Database and configuration
├── frontend/              # React TypeScript frontend
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Build configuration
└── SETUP_AND_RUN_GUIDE.md # This file
```

## 🌟 Features

- **Interactive Map**: Click anywhere to analyze site readiness
- **Real-time Analysis**: Get instant scores and recommendations
- **Multiple Use Cases**: Supports retail, office, warehouse, restaurant, residential, industrial
- **Comprehensive Scoring**: 5-category analysis (demographics, transport, infrastructure, market, environment)
- **Professional UI**: Clean, responsive interface with detailed results

## 🔄 Development Workflow

### Making Changes

**Backend Changes:**
- Edit files in `backend/` directory
- Server auto-reloads with `--reload` flag
- Check logs in terminal for errors

**Frontend Changes:**
- Edit files in `frontend/src/` directory
- Vite provides hot module replacement
- Changes appear instantly in browser

### Adding New Features
1. Update backend API in `backend/api/routes/`
2. Update frontend components in `frontend/src/components/`
3. Test changes using the browser interface

## 📝 Common Commands

### Backend Commands
```bash
cd backend

# Start development server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Install new Python package
pip install package_name
pip freeze > requirements.txt

# Check database health
python -c "from core.database import comprehensive_health_check; import asyncio; print(asyncio.run(comprehensive_health_check()))"
```

### Frontend Commands
```bash
cd frontend

# Start development server
npm run dev

# Install new package
npm install package_name

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎯 Success Indicators

✅ **Backend Running Successfully:**
- Terminal shows: "Application startup complete"
- Health check returns: `http://localhost:8000/health`
- API docs accessible: `http://localhost:8000/docs`

✅ **Frontend Running Successfully:**
- Terminal shows: "Local: http://localhost:3000"
- Browser loads the map interface
- No console errors in browser (F12)

✅ **Full System Working:**
- Map loads and displays Ahmedabad area
- Clicking on map shows "Analyzing location..." message
- Results panel shows score and analysis data
- Different locations return different scores

## 🆘 Getting Help

### Check Logs
- **Backend logs**: Check the terminal running the Python server
- **Frontend logs**: Check browser console (F12 → Console tab)
- **Network issues**: Check browser Network tab (F12 → Network)

### Common Error Solutions
- **CORS errors**: Backend CORS is configured to allow all origins
- **Connection refused**: Ensure backend is running on correct port
- **Module errors**: Reinstall dependencies with `pip install -r requirements.txt`
- **Map tiles not loading**: Check internet connection

## 🎉 You're Ready!

Once both servers are running:
1. Open `http://localhost:3000` in your browser
2. Click anywhere on the map
3. View the comprehensive site analysis results
4. Explore different locations to see varying scores

**Enjoy analyzing geospatial site readiness! 🌍📊**