# ⚡ Quick Start Guide

## 🚀 Start the Application (2 minutes)

### Step 1: Start Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
✅ Backend ready at: http://localhost:8000

### Step 2: Start Frontend
```bash
cd frontend
npm run dev
```
✅ Frontend ready at: http://localhost:3001

---

## 🎮 Use the Application (30 seconds)

### Option 1: Click on Map
1. Open http://localhost:3001
2. Click anywhere on the map
3. View score popup

### Option 2: Search Coordinates
1. Enter latitude: `23.0225`
2. Enter longitude: `72.5714`
3. Click "🔍 Analyze Location"

### Option 3: Quick Locations
1. Click "📍 Center" button
2. Wait for analysis
3. View results

---

## 📊 Understanding Scores

### Score Range
- **80-100**: Excellent ⭐⭐⭐⭐⭐
- **60-79**: Good ⭐⭐⭐⭐
- **40-59**: Fair ⭐⭐⭐
- **20-39**: Poor ⭐⭐
- **0-19**: Very Poor ⭐

### Score Layers
- 📊 **Demographics** (35%): Population, income, age
- 🚗 **Transport** (25%): Road access, highways
- 🏪 **POI** (20%): Competitors, anchors, services
- 🏗️ **Land Use** (10%): Zoning, development
- 🌳 **Environment** (10%): Risks, air quality

---

## 🔧 Troubleshooting (1 minute)

### Map Not Loading?
```bash
# Check internet connection (map tiles from OpenStreetMap)
# Refresh browser (Ctrl+R)
```

### API Error?
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check backend logs in terminal
```

### Frontend Error?
```bash
# Check frontend terminal for errors
# Restart frontend: Ctrl+C, then npm run dev
```

---

## 📍 Example Locations to Try

| Location | Lat | Lng | Expected Score |
|----------|-----|-----|----------------|
| City Center | 23.0225 | 72.5714 | ~67 |
| North Area | 23.0825 | 72.5714 | ~67 |
| South Area | 22.9625 | 72.5714 | ~67 |
| East Area | 23.0225 | 72.6314 | ~67 |
| West Area | 23.0225 | 72.5114 | ~67 |

---

## 🎯 Quick Demo Script (2 minutes)

### Minute 1: Introduction
"This is a geospatial site readiness analyzer for commercial real estate. It scores locations across 5 dimensions: demographics, transport, POI, land use, and environment."

### Minute 2: Live Demo
1. Click on map: "Click anywhere to analyze"
2. Show popup: "See detailed breakdown"
3. Try coordinates: "Or search precise locations"
4. Quick location: "Or use quick presets"

---

## 📚 Full Documentation

- **README.md** - Complete project overview
- **USER_GUIDE.md** - Detailed user instructions
- **DEMO_GUIDE.md** - 5-minute presentation script
- **PROJECT_STATUS.md** - Current status and metrics
- **API Docs** - http://localhost:8000/docs

---

## ✅ Pre-Demo Checklist

- [ ] Backend running (http://localhost:8000)
- [ ] Frontend running (http://localhost:3001)
- [ ] Map loads correctly
- [ ] Click-to-analyze works
- [ ] Coordinate search works
- [ ] No errors in console

---

## 🆘 Emergency Contacts

### If Something Breaks

1. **Check both terminals** for error messages
2. **Restart backend**: Ctrl+C, then re-run uvicorn command
3. **Restart frontend**: Ctrl+C, then npm run dev
4. **Check API directly**: http://localhost:8000/docs
5. **Review logs**: Look for red error messages

### Common Fixes

```bash
# Backend not responding
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend not compiling
cd frontend
rm -rf node_modules
npm install
npm run dev

# Database issues
cd backend
python data_pipeline/run_all.py
```

---

## 🎉 You're Ready!

**Everything is set up and working. Just follow the steps above to start using the application.**

**Need help?** Check USER_GUIDE.md for detailed instructions.

**Want to present?** Check DEMO_GUIDE.md for a 5-minute script.

---

**Built with ❤️ for intelligent location analysis**
