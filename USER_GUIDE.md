# 📖 User Guide - GeoSpatial Site Readiness Analyzer

## Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Analyzing Locations](#analyzing-locations)
4. [Understanding Scores](#understanding-scores)
5. [Tips & Best Practices](#tips--best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing the Application

1. **Open your web browser** (Chrome, Firefox, Safari, or Edge)
2. **Navigate to**: `http://localhost:3001`
3. **Wait for the map to load** (you should see OpenStreetMap tiles)

### First Look

When you first open the application, you'll see:
- 🗺️ **Interactive map** centered on Ahmedabad, Gujarat
- 📋 **Control panel** on the left with coordinate inputs
- 🧭 **Navigation controls** on the top-right of the map
- 📏 **Scale bar** at the bottom-right

---

## Interface Overview

### Control Panel (Left Side)

The control panel is your main interaction point:

```
┌─────────────────────────────────┐
│ 🌍 GeoSpatial Site Analyzer    │
├─────────────────────────────────┤
│ Latitude:  [23.0225]            │
│ Longitude: [72.5714]            │
│                                 │
│ [🔍 Analyze Location]           │
├─────────────────────────────────┤
│ Quick Locations:                │
│ [📍 Center] [📍 North] [📍 South]│
├─────────────────────────────────┤
│ 💡 Tip: Click anywhere on map   │
└─────────────────────────────────┘
```

### Map Controls (Top-Right)

- **➕ Zoom In**: Increase map zoom level
- **➖ Zoom Out**: Decrease map zoom level
- **🧭 Reset North**: Rotate map to north-up orientation

### Score Display (Bottom-Left)

After analyzing a location, you'll see:
```
┌─────────────────┐
│ Current Site    │
│ Score           │
│                 │
│     66.7        │
│                 │
│ out of 100      │
└─────────────────┘
```

---

## Analyzing Locations

### Method 1: Click on Map (Recommended)

This is the fastest way to analyze any location:

1. **Click anywhere** on the map
2. **Wait 1-2 seconds** for analysis
3. **View the popup** with detailed scores
4. **Blue marker** appears at clicked location

**Example:**
- Click on a busy commercial area
- Click on a residential neighborhood
- Click near major roads or highways

### Method 2: Enter Coordinates

For precise location analysis:

1. **Enter Latitude** in the first input box
   - Example: `23.0225`
   - Range: -90 to 90
   - Positive = North, Negative = South

2. **Enter Longitude** in the second input box
   - Example: `72.5714`
   - Range: -180 to 180
   - Positive = East, Negative = West

3. **Click "🔍 Analyze Location"**

4. **Map flies to location** with smooth animation

5. **Analysis popup appears** after 2 seconds

**Validation:**
- ✅ Valid: `23.0225, 72.5714`
- ❌ Invalid: `abc, xyz` (shows error message)
- ❌ Invalid: `95, 200` (out of range)

### Method 3: Quick Locations

For rapid testing of different areas:

1. **Click "📍 Center"** - Analyzes Ahmedabad city center
2. **Click "📍 North"** - Analyzes northern area
3. **Click "📍 South"** - Analyzes southern area

Each button:
- Updates coordinate inputs
- Flies to location
- Automatically analyzes after 2 seconds

---

## Understanding Scores

### Popup Breakdown

When you analyze a location, you see:

```
┌──────────────────────────────────────┐
│ 📍 Site Analysis                     │
├──────────────────────────────────────┤
│         Composite Score              │
│                                      │
│            66.7                      │
│                                      │
│         out of 100                   │
├──────────────────────────────────────┤
│ 📊 Demographics        54.4          │
│ 🚗 Transport           80.0          │
│ 🏪 Points of Interest  68.0          │
│ 🏗️ Land Use            72.7          │
│ 🌳 Environment         68.0          │
├──────────────────────────────────────┤
│ 📍 23.0225°N, 72.5714°E              │
└──────────────────────────────────────┘
```

### Score Interpretation

#### Composite Score (0-100)
- **80-100**: Excellent site - Highly recommended
- **60-79**: Good site - Suitable with minor considerations
- **40-59**: Fair site - Requires careful evaluation
- **20-39**: Poor site - Significant challenges
- **0-19**: Very poor site - Not recommended

#### Layer Scores

**📊 Demographics (35% weight)**
- Measures: Population density, median income, working-age percentage
- High score = Dense, affluent, working-age population
- Best for: Retail, restaurants, services

**🚗 Transport (25% weight)**
- Measures: Highway access, arterial roads, local connectivity
- High score = Excellent road access and connectivity
- Best for: Logistics, retail, offices

**🏪 Points of Interest (20% weight)**
- Measures: Competitor distance, anchor stores, complementary services
- High score = Good anchor proximity, manageable competition
- Best for: Retail, restaurants

**🏗️ Land Use (10% weight)**
- Measures: Zoning compatibility, development potential
- High score = Commercial/mixed-use zoning, development ready
- Best for: New construction, redevelopment

**🌳 Environment (10% weight)**
- Measures: Flood risk, earthquake risk, air quality
- High score = Low environmental risks
- Best for: All use cases (safety factor)

### Real-World Examples

**Example 1: High-Scoring Location (Score: 85)**
```
Demographics: 90 → Dense, affluent area
Transport: 95 → Near highway interchange
POI: 80 → Good anchor stores, low competition
Land Use: 75 → Commercial zoning
Environment: 70 → Moderate air quality
```
**Recommendation**: Excellent for premium retail or restaurant

**Example 2: Medium-Scoring Location (Score: 55)**
```
Demographics: 45 → Lower income area
Transport: 60 → Moderate road access
POI: 50 → High competition
Land Use: 65 → Mixed-use zoning
Environment: 55 → Some flood risk
```
**Recommendation**: Consider for budget retail or warehouse

---

## Tips & Best Practices

### For Retail Site Selection

1. **Look for scores 70+** in Demographics and POI layers
2. **Check Transport score** for customer accessibility
3. **Analyze multiple locations** in the same area
4. **Compare scores** across different neighborhoods

### For Office Space

1. **Prioritize Transport score** (employee commute)
2. **Demographics score 60+** for talent pool
3. **Environment score** matters for employee wellbeing
4. **POI score** less critical than retail

### For Warehouse/Logistics

1. **Transport score is critical** (80+ recommended)
2. **Land Use score** for zoning compatibility
3. **Demographics less important**
4. **Environment score** for operational safety

### General Tips

✅ **Do:**
- Analyze multiple locations before deciding
- Consider all 5 layers, not just composite score
- Use Quick Locations to understand score ranges
- Check coordinates are within study area (Ahmedabad)

❌ **Don't:**
- Rely solely on composite score
- Ignore low Environment scores (safety risk)
- Compare scores across different cities (not supported yet)
- Expect real-time data (uses synthetic data)

---

## Troubleshooting

### Map Not Loading

**Problem**: Blank white screen or no map tiles

**Solutions:**
1. Check internet connection (map tiles load from OpenStreetMap)
2. Refresh the page (Ctrl+R or Cmd+R)
3. Clear browser cache
4. Try a different browser

### "Error analyzing location" Message

**Problem**: API call fails

**Solutions:**
1. Check backend is running: `http://localhost:8000/health`
2. Verify coordinates are within study area (Ahmedabad)
3. Check browser console for detailed error
4. Restart backend server

### Coordinates Not Working

**Problem**: "Please enter valid coordinates" error

**Solutions:**
1. Ensure latitude is between -90 and 90
2. Ensure longitude is between -180 and 180
3. Use decimal format (e.g., `23.0225`, not `23° 1' 21"`)
4. Don't include letters or special characters

### Popup Not Appearing

**Problem**: Click on map but no popup shows

**Solutions:**
1. Wait 2-3 seconds (API call in progress)
2. Check for loading indicator
3. Look for error message in control panel
4. Verify backend is responding: `http://localhost:8000/docs`

### Slow Performance

**Problem**: Analysis takes too long

**Solutions:**
1. Check backend logs for errors
2. Verify database has data: `SELECT COUNT(*) FROM h3_hex_scores;`
3. Restart backend server
4. Close other browser tabs

### Score Seems Wrong

**Problem**: Unexpected score values

**Solutions:**
1. Remember: This uses synthetic data (not real-world data)
2. Check all 5 layer scores, not just composite
3. Verify location is within Ahmedabad study area
4. Understand scoring methodology (see README.md)

---

## Keyboard Shortcuts

- **Ctrl/Cmd + Click**: Analyze location (same as regular click)
- **+/-**: Zoom in/out (when map is focused)
- **Arrow Keys**: Pan map (when map is focused)
- **Shift + Drag**: Rotate map
- **Ctrl/Cmd + Drag**: Pitch map (3D tilt)

---

## Advanced Usage

### Analyzing a Grid of Locations

To systematically analyze an area:

1. Start at one corner (e.g., `23.00, 72.50`)
2. Analyze and note score
3. Move 0.01 degrees (e.g., `23.01, 72.50`)
4. Repeat to create a grid
5. Identify highest-scoring locations

### Comparing Locations

To compare two locations:

1. Analyze first location, note scores
2. Take screenshot or write down scores
3. Analyze second location
4. Compare layer-by-layer
5. Consider trade-offs (e.g., higher demographics vs. lower transport)

### Finding Optimal Sites

Strategy for finding best sites:

1. **Broad Search**: Click around entire study area
2. **Identify Clusters**: Find areas with consistently high scores
3. **Detailed Analysis**: Use coordinate search for precision
4. **Layer Analysis**: Check which layers drive high scores
5. **Validation**: Analyze nearby locations to confirm pattern

---

## Data Limitations

### Current Limitations

⚠️ **Synthetic Data**: All data is computer-generated for demonstration
⚠️ **Static Data**: No real-time updates (traffic, events, etc.)
⚠️ **Single City**: Only Ahmedabad, Gujarat is supported
⚠️ **No Historical Data**: Cannot analyze trends over time
⚠️ **Simplified Scoring**: Real-world decisions require more factors

### Future Enhancements

Coming soon:
- Real-world data integration
- Multi-city support
- Historical trend analysis
- Custom weight configuration
- Batch location analysis
- PDF report generation

---

## Getting Help

### Resources

1. **API Documentation**: `http://localhost:8000/docs`
2. **README**: See `README.md` for technical details
3. **Demo Guide**: See `DEMO_GUIDE.md` for presentation tips
4. **Troubleshooting**: See `TROUBLESHOOTING.md` for common issues

### Support Channels

- Check browser console (F12) for errors
- Review backend logs in terminal
- Inspect network tab for API failures
- Test API directly using `/docs` interface

---

## Glossary

**Composite Score**: Weighted average of all 5 layer scores

**H3 Hexagon**: Hexagonal spatial index used for efficient scoring

**Layer Score**: Individual score for one dimension (demographics, transport, etc.)

**POI**: Point of Interest (stores, restaurants, services, etc.)

**Study Area**: Geographic region covered by the analysis (Ahmedabad)

**Weight**: Importance factor for each layer (demographics=35%, transport=25%, etc.)

**WKT**: Well-Known Text format for storing geometry in SQLite

---

**Happy Analyzing! 🎯**

For technical support, check the backend logs and API documentation.
