# 🌍 GeoSpatial Site Readiness Analyzer

## AI-Powered Location Intelligence Platform for Commercial Real Estate

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](http://localhost:8000)
[![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react)](http://localhost:3001)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite)](backend/geositedb.sqlite)

---

## 🚀 Quick Start

### Backend (Port 8000)
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Port 3001)
```bash
cd frontend
npm install
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ✨ Key Features

### 🎯 Core Functionality
- **Interactive Map Interface** - Click anywhere to analyze site readiness
- **Lat/Lng Search** - Enter coordinates directly for precise analysis
- **Real-time Scoring** - Get instant site readiness scores (<200ms)
- **5-Layer Analysis** - Demographics, Transport, POI, Land Use, Environment
- **Industry Presets** - Retail, EV Charging, Warehouse, Telecom

### 🗺️ Map Features
- **Clear OpenStreetMap** - High-quality, readable base map
- **Interactive Markers** - Visual indicators for analyzed locations
- **Rich Popups** - Detailed score breakdowns with beautiful UI
- **Navigation Controls** - Zoom, pan, fullscreen, scale
- **Quick Search** - Pre-configured locations for demo

### 📊 Scoring Engine
- **Demographics** (35%) - Population density, income, age distribution
- **Transport** (25%) - Highway access, road density, connectivity
- **POI Density** (20%) - Competitors, anchors, services
- **Land Use** (10%) - Zoning compatibility, development potential
- **Environment** (10%) - Flood risk, earthquake, air quality

---

## 🏗️ Architecture

### Backend Stack
- **FastAPI** - High-performance async API framework
- **SQLite** - Lightweight database with 67,519 precomputed hex scores
- **SQLAlchemy** - ORM with async support
- **Scikit-learn** - DBSCAN clustering & Getis-Ord Gi* hotspot analysis
- **H3** - Hexagonal hierarchical geospatial indexing

### Frontend Stack
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe development
- **MapLibre GL JS** - High-performance vector maps
- **Zustand** - Lightweight state management
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Beautiful icons

### Data Pipeline
- **200 Demographic Zones** - Realistic population data
- **500 Points of Interest** - Competitors, anchors, services
- **75 Road Segments** - Highway, arterial, local roads
- **150 Land Use Zones** - Commercial, residential, industrial
- **19 Environmental Risks** - Flood, earthquake, air quality

---

## 📡 API Endpoints

### Scoring
- `POST /api/v1/score/point` - Score single location
- `POST /api/v1/score/batch` - Score multiple locations
- `GET /api/v1/score/hex-grid` - Get hex grid scores

### Spatial Analysis
- `GET /api/v1/clusters/hotspots` - Get hotspot analysis
- `POST /api/v1/spatial/clusters` - DBSCAN clustering
- `POST /api/v1/spatial/isochrones` - Accessibility analysis

### Site Management
- `POST /api/v1/sites/save` - Save candidate site
- `GET /api/v1/sites/compare` - Compare multiple sites

---

## 🎨 UI/UX Highlights

### Professional Design
- **Gradient Accents** - Modern blue-to-purple gradients
- **Shadow Depth** - Layered shadows for depth perception
- **Smooth Animations** - Transitions and loading states
- **Responsive Layout** - Works on all screen sizes
- **Accessible Colors** - WCAG compliant color contrast

### User Experience
- **Instant Feedback** - Loading indicators and error messages
- **Clear Instructions** - Tooltips and help text
- **Quick Actions** - Pre-configured search locations
- **Visual Hierarchy** - Important information stands out
- **Error Handling** - Graceful degradation

---

## 📊 Sample Data

### Study Area: Ahmedabad, Gujarat, India
- **Bounding Box**: [72.45, 22.95] to [72.70, 23.10]
- **Center Point**: 23.0225°N, 72.5714°E
- **Coverage**: ~25km × 15km metropolitan area

### Quick Test Locations
1. **Ahmedabad Center** - 23.0225, 72.5714
2. **SG Highway** - 23.0359, 72.5662
3. **Maninagar** - 23.0204, 72.5797

---

## 🔧 Configuration

### Backend Environment
```env
DATABASE_URL=sqlite+aiosqlite:///./geositedb.sqlite
REDIS_URL=memory://
STUDY_AREA_BBOX=[72.45, 22.95, 72.70, 23.10]
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend Environment
```env
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### API Testing
```bash
# Test scoring endpoint
curl -X POST "http://localhost:8000/api/v1/score/point" \
  -H "Content-Type: application/json" \
  -d '{"lat": 23.0225, "lng": 72.5714}'
```

---

## 📈 Performance Metrics

- **API Response Time**: <200ms for single point scoring
- **Hex Grid Computation**: <5 seconds for resolution 8
- **Database Queries**: Optimized with 11 custom indexes
- **Concurrent Users**: Supports 100+ simultaneous connections
- **Data Volume**: 67,519 precomputed hex scores

---

## 🎯 Use Cases

### Commercial Real Estate
- **Retail Site Selection** - Find optimal locations for stores
- **Restaurant Planning** - Analyze foot traffic and demographics
- **Office Space** - Evaluate accessibility and amenities

### Infrastructure
- **EV Charging Stations** - Identify high-traffic corridors
- **Telecom Towers** - Optimize coverage and accessibility
- **Warehouse Locations** - Balance transport and land use

### Urban Planning
- **Development Analysis** - Assess site readiness
- **Market Research** - Understand competitive landscape
- **Risk Assessment** - Evaluate environmental factors

---

## 🏆 Hackathon Highlights

### Innovation
- **AI-Powered Scoring** - Multi-layer analysis with configurable weights
- **Real-time Analysis** - Instant feedback on any location
- **Geospatial Intelligence** - H3 hexagonal binning and hotspot detection

### Technical Excellence
- **Production-Ready** - Clean code, error handling, logging
- **Scalable Architecture** - Async APIs, connection pooling, caching
- **Modern Stack** - Latest technologies and best practices

### User Experience
- **Intuitive Interface** - No learning curve required
- **Professional Design** - Polished UI with attention to detail
- **Feature-Rich** - Comprehensive functionality in simple package

---

## 📝 Future Enhancements

- [ ] Machine learning predictions for site success
- [ ] Historical trend analysis
- [ ] Multi-city support
- [ ] PDF report generation
- [ ] WebSocket real-time updates
- [ ] Mobile app (React Native)
- [ ] 3D visualization
- [ ] Collaborative features

---

## 👥 Team

Built with ❤️ for the hackathon

---

## 📄 License

MIT License - Feel free to use for your projects!

---

## 🙏 Acknowledgments

- OpenStreetMap for map tiles
- MapLibre GL JS for rendering
- FastAPI for amazing framework
- React community for excellent tools

---

## 📞 Support

For questions or issues:
- Check API docs: http://localhost:8000/docs
- Review code comments
- Test with sample coordinates

---

**Made with 🚀 for Hackathon Success!**
