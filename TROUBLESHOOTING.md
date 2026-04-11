# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Frontend Issues

#### Map Not Visible / Blank Screen
**Solution**:
1. Check browser console (F12) for errors
2. Verify frontend is running: http://localhost:3001
3. Clear browser cache (Ctrl+Shift+R)
4. Check if MapLibre CSS is loaded

#### "Failed to fetch score" Error
**Solution**:
1. Verify backend is running: http://localhost:8000/health
2. Check CORS settings in backend
3. Verify coordinates are within study area (Ahmedabad)
4. Check browser network tab for API errors

#### Coordinates Search Not Working
**Solution**:
1. Ensure latitude is between -90 and 90
2. Ensure longitude is between -180 and 180
3. Use decimal format (e.g., 23.0225, not 23°01'21")
4. Check for typos in input

---

### Backend Issues

#### Port 8000 Already in Use
**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

#### Database Not Found
**Solution**:
```bash
cd backend
python data_pipeline/run_all.py
```

#### Import Errors
**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

#### Slow API Responses
**Solution**:
1. Check database indexes: Should see 11 indexes
2. Verify data is loaded: Check geositedb.sqlite size
3. Restart backend to clear any issues

---

### Installation Issues

#### npm install Fails
**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Python Dependencies Fail
**Solution**:
```bash
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

---

### Performance Issues

#### Map Loads Slowly
**Solution**:
1. Check internet connection (map tiles from OpenStreetMap)
2. Try different map style
3. Reduce initial zoom level

#### API Takes >1 Second
**Solution**:
1. Verify database has indexes
2. Check if data pipeline completed
3. Restart backend server
4. Check system resources (CPU/RAM)

---

### Data Issues

#### No Scores Returned
**Solution**:
1. Verify data pipeline ran successfully
2. Check database has records:
```bash
sqlite3 backend/geositedb.sqlite "SELECT COUNT(*) FROM demographic_zones;"
```
3. Re-run data pipeline if needed

#### Scores All Zero
**Solution**:
1. Check if coordinates are in study area
2. Verify scoring engine is working:
```bash
cd backend
python test_scoring.py
```

---

### Browser Compatibility

#### Works in Chrome but not Firefox/Safari
**Solution**:
1. Update browser to latest version
2. Enable JavaScript
3. Check browser console for specific errors
4. Try incognito/private mode

---

### Quick Fixes

#### Complete Reset
```bash
# Stop all servers
# Delete database
rm backend/geositedb.sqlite

# Regenerate data
cd backend
python data_pipeline/run_all.py

# Restart backend
python -m uvicorn main:app --reload

# Restart frontend
cd ../frontend
npm run dev
```

#### Clear All Caches
```bash
# Frontend
cd frontend
rm -rf node_modules .vite
npm install

# Backend
cd backend
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

### Verification Checklist

Before demo, verify:
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3001
- [ ] Health endpoint returns "healthy"
- [ ] Map loads and displays
- [ ] Click on map shows popup
- [ ] Coordinate search works
- [ ] Quick search buttons work
- [ ] Scores display correctly
- [ ] No console errors

---

### Emergency Backup Plan

If nothing works during demo:
1. Show API documentation: http://localhost:8000/docs
2. Demonstrate with curl commands
3. Show code walkthrough
4. Present architecture diagrams
5. Discuss technical approach

---

### Getting Help

1. Check browser console (F12)
2. Check backend logs in terminal
3. Verify all services running
4. Test with curl/Postman
5. Review error messages carefully

---

### Performance Optimization

If system is slow:
```bash
# Backend
- Reduce data volume
- Add more indexes
- Use connection pooling
- Enable caching

# Frontend
- Reduce map complexity
- Lazy load components
- Optimize images
- Minimize bundle size
```

---

## 🎯 Pre-Demo Checklist

30 minutes before:
- [ ] Test full workflow
- [ ] Clear browser cache
- [ ] Restart both servers
- [ ] Test on actual demo machine
- [ ] Have backup browser ready
- [ ] Screenshot working state
- [ ] Note down test coordinates
- [ ] Prepare fallback demo

---

## 📞 Quick Commands

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend is running
curl http://localhost:3001

# Test scoring API
curl -X POST http://localhost:8000/api/v1/score/point \
  -H "Content-Type: application/json" \
  -d '{"lat": 23.0225, "lng": 72.5714}'

# Check database
sqlite3 backend/geositedb.sqlite "SELECT COUNT(*) FROM h3_hex_scores;"
```

---

**Remember**: Stay calm, have backups ready, and focus on what works! 🚀
