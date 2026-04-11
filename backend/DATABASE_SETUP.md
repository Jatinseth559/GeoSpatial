# PostgreSQL Database Setup with PostGIS Extension

This document describes the comprehensive PostgreSQL database setup for the GeoSpatial Site Readiness Analyzer, including PostGIS spatial extension, optimized indexing, and performance configurations.

## Overview

The system uses PostgreSQL 15 with PostGIS 3.3 extension to provide robust spatial data storage and analysis capabilities. The database is optimized for high-performance geospatial queries with comprehensive spatial indexing and connection pooling.

## Database Schema

### Core Spatial Tables

#### 1. Demographic Zones (`demographic_zones`)
Stores demographic and socioeconomic data for analysis zones.

```sql
CREATE TABLE demographic_zones (
    id SERIAL PRIMARY KEY,
    zone_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200),
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    population INTEGER,
    population_density FLOAT,
    median_income FLOAT,
    median_age FLOAT,
    youth_population_pct FLOAT,
    working_age_pct FLOAT,
    household_count INTEGER,
    data_year INTEGER DEFAULT 2023,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. Road Network (`road_network`)
Contains road infrastructure data for accessibility analysis.

```sql
CREATE TABLE road_network (
    id SERIAL PRIMARY KEY,
    osm_id NUMERIC(20),
    road_type VARCHAR(50),
    name VARCHAR(200),
    geom GEOMETRY(LINESTRING, 4326) NOT NULL,
    lanes INTEGER,
    max_speed INTEGER,
    is_highway BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. Points of Interest (`points_of_interest`)
Stores POI data including competitors, anchors, and services.

```sql
CREATE TABLE points_of_interest (
    id SERIAL PRIMARY KEY,
    poi_id VARCHAR(100) UNIQUE,
    name VARCHAR(300),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    geom GEOMETRY(POINT, 4326) NOT NULL,
    brand VARCHAR(200),
    is_competitor BOOLEAN DEFAULT FALSE,
    is_anchor BOOLEAN DEFAULT FALSE,
    rating FLOAT,
    review_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. Land Use Zones (`land_use_zones`)
Contains zoning and land use compatibility data.

```sql
CREATE TABLE land_use_zones (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(50),
    zone_type VARCHAR(100),
    description TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    allows_retail BOOLEAN DEFAULT FALSE,
    allows_warehouse BOOLEAN DEFAULT FALSE,
    floor_area_ratio FLOAT,
    max_building_height FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 5. Environmental Risks (`environmental_risks`)
Stores environmental risk factors and hazard zones.

```sql
CREATE TABLE environmental_risks (
    id SERIAL PRIMARY KEY,
    risk_id VARCHAR(100),
    risk_type VARCHAR(100),
    severity VARCHAR(50),
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    flood_zone_code VARCHAR(20),
    earthquake_pga FLOAT,
    air_quality_index FLOAT,
    data_source VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 6. Candidate Sites (`candidate_sites`)
Stores analyzed candidate locations with scores and isochrones.

```sql
CREATE TABLE candidate_sites (
    id SERIAL PRIMARY KEY,
    site_name VARCHAR(300),
    description TEXT,
    geom GEOMETRY(POINT, 4326) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    composite_score FLOAT,
    score_breakdown JSONB,
    weights_used JSONB,
    isochrone_10min GEOMETRY(POLYGON, 4326),
    isochrone_20min GEOMETRY(POLYGON, 4326),
    isochrone_30min GEOMETRY(POLYGON, 4326),
    catchment_pop_10min INTEGER,
    catchment_pop_20min INTEGER,
    catchment_pop_30min INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Spatial Indexing Strategy

### Primary GIST Indexes
All geometry columns have GIST spatial indexes for optimal query performance:

```sql
-- Core spatial indexes (automatically created by SQLAlchemy models)
CREATE INDEX idx_demographic_zones_geom ON demographic_zones USING GIST (geom);
CREATE INDEX idx_road_network_geom ON road_network USING GIST (geom);
CREATE INDEX idx_poi_geom ON points_of_interest USING GIST (geom);
CREATE INDEX idx_land_use_geom ON land_use_zones USING GIST (geom);
CREATE INDEX idx_env_risk_geom ON environmental_risks USING GIST (geom);
CREATE INDEX idx_candidate_sites_geom ON candidate_sites USING GIST (geom);
```

### Enhanced Composite Indexes
Additional indexes for common query patterns:

```sql
-- Demographic analysis indexes
CREATE INDEX idx_demographic_zones_density_income ON demographic_zones (population_density, median_income);

-- POI analysis indexes
CREATE INDEX idx_poi_category_competitor ON points_of_interest (category, is_competitor);
CREATE INDEX idx_poi_category_anchor ON points_of_interest (category, is_anchor);

-- Road network indexes
CREATE INDEX idx_road_network_type_highway ON road_network (road_type, is_highway);

-- Land use indexes
CREATE INDEX idx_land_use_retail_warehouse ON land_use_zones (allows_retail, allows_warehouse);

-- Environmental risk indexes
CREATE INDEX idx_env_risk_type_severity ON environmental_risks (risk_type, severity);

-- Isochrone spatial indexes
CREATE INDEX idx_candidate_sites_isochrone_10min ON candidate_sites USING GIST (isochrone_10min);
CREATE INDEX idx_candidate_sites_isochrone_20min ON candidate_sites USING GIST (isochrone_20min);
CREATE INDEX idx_candidate_sites_isochrone_30min ON candidate_sites USING GIST (isochrone_30min);
```

## Connection Pooling Configuration

The system uses SQLAlchemy's async connection pooling with the following settings:

```python
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,      # Validate connections before use
    pool_size=20,            # Base connection pool size
    max_overflow=10,         # Additional connections under load
)
```

### Pool Settings Explanation:
- **pool_size=20**: Base number of connections maintained in the pool
- **max_overflow=10**: Additional connections created under high load (total max: 30)
- **pool_pre_ping=True**: Validates connections before use to handle disconnections

## Health Check Implementation

### Basic Health Check Endpoint
```
GET /health
```

Returns comprehensive health status including:
- Database connectivity
- PostGIS extension availability
- Table existence and data population
- Spatial index status
- Redis connectivity

### Comprehensive Health Check Function
The `comprehensive_health_check()` function validates:

1. **Database Connection**: Tests basic connectivity
2. **PostGIS Availability**: Verifies spatial extension is loaded
3. **Table Existence**: Confirms all required tables are created
4. **Spatial Indexes**: Validates GIST indexes are active
5. **Data Population**: Checks if synthetic data is loaded
6. **Redis Connection**: Tests cache connectivity

## Performance Optimizations

### PostgreSQL Settings
Applied automatically during database initialization:

```sql
-- Increase work memory for spatial operations
SET work_mem = '256MB';

-- Optimize for spatial queries
SET random_page_cost = 1.1;
SET seq_page_cost = 1.0;

-- Enable parallel query execution
SET max_parallel_workers_per_gather = 4;
SET parallel_tuple_cost = 0.1;
SET parallel_setup_cost = 1000.0;

-- Optimize cache settings
SET effective_cache_size = '1GB';
```

### Custom Spatial Functions
The system creates optimized spatial functions:

```sql
-- Distance calculation in kilometers
CREATE OR REPLACE FUNCTION distance_km(geom1 geometry, geom2 geometry)
RETURNS double precision AS $$
BEGIN
    RETURN ST_Distance(ST_Transform(geom1, 3857), ST_Transform(geom2, 3857)) / 1000.0;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Study area validation
CREATE OR REPLACE FUNCTION is_within_study_area(geom geometry)
RETURNS boolean AS $$
BEGIN
    RETURN ST_Within(geom, ST_MakeEnvelope(72.45, 22.87, 72.75, 23.15, 4326));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Population within radius calculation
CREATE OR REPLACE FUNCTION population_within_radius(center_geom geometry, radius_km double precision)
RETURNS integer AS $$
DECLARE
    total_pop integer := 0;
BEGIN
    SELECT COALESCE(SUM(population), 0) INTO total_pop
    FROM demographic_zones
    WHERE ST_DWithin(ST_Transform(geom, 3857), ST_Transform(center_geom, 3857), radius_km * 1000);
    
    RETURN total_pop;
END;
$$ LANGUAGE plpgsql STABLE;
```

### Materialized Views
Pre-computed views for common queries:

```sql
-- High-density zones for POI clustering
CREATE MATERIALIZED VIEW high_density_zones AS
SELECT zone_id, name, geom, population_density, median_income, ST_Centroid(geom) as centroid
FROM demographic_zones
WHERE population_density > (
    SELECT percentile_cont(0.75) WITHIN GROUP (ORDER BY population_density)
    FROM demographic_zones
);

-- Major roads for accessibility calculations
CREATE MATERIALIZED VIEW major_roads AS
SELECT id, road_type, name, geom, is_highway, max_speed
FROM road_network
WHERE road_type IN ('motorway', 'primary', 'secondary') OR is_highway = true;

-- Commercial zones for site analysis
CREATE MATERIALIZED VIEW commercial_zones AS
SELECT id, zone_code, zone_type, geom, floor_area_ratio, max_building_height
FROM land_use_zones
WHERE allows_retail = true OR zone_type = 'commercial';
```

## Docker Configuration

### PostgreSQL Container
```yaml
postgres:
  image: postgis/postgis:15-3.3
  environment:
    POSTGRES_DB: geositedb
    POSTGRES_USER: geosite
    POSTGRES_PASSWORD: geosite_pass
  healthcheck:
    test: ["CMD", "pg_isready", "-U", "geosite"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Service Dependencies
```yaml
backend:
  depends_on:
    postgres:
      condition: service_healthy  # Wait for PostgreSQL to be ready
```

## Validation and Testing

### Database Setup Validation
Run the validation script to ensure proper setup:

```bash
cd backend
python validate_db_setup.py
```

The validation script checks:
- PostgreSQL and PostGIS versions
- Table creation and geometry columns
- Spatial index existence and functionality
- Connection pooling performance
- Custom spatial functions
- Overall system health

### Performance Testing
The system includes performance validation for:
- Spatial index utilization in queries
- Connection pool efficiency under load
- Query response times for common operations

## Troubleshooting

### Common Issues

1. **PostGIS Extension Not Found**
   ```sql
   -- Manually create extension if needed
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE EXTENSION IF NOT EXISTS postgis_topology;
   ```

2. **Spatial Index Not Used**
   ```sql
   -- Check if spatial indexes exist
   SELECT indexname, indexdef FROM pg_indexes 
   WHERE tablename = 'your_table' AND indexdef LIKE '%gist%';
   
   -- Analyze table statistics
   ANALYZE your_table;
   ```

3. **Connection Pool Exhaustion**
   - Monitor active connections: `SELECT count(*) FROM pg_stat_activity;`
   - Adjust pool_size and max_overflow in database.py
   - Check for connection leaks in application code

4. **Poor Spatial Query Performance**
   ```sql
   -- Check query execution plan
   EXPLAIN (ANALYZE, BUFFERS) 
   SELECT * FROM points_of_interest 
   WHERE ST_DWithin(geom, ST_Point(72.5, 23.0), 0.01);
   ```

### Monitoring Queries

```sql
-- Check spatial index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%geom%'
ORDER BY idx_scan DESC;

-- Monitor connection pool
SELECT state, count(*) 
FROM pg_stat_activity 
WHERE datname = 'geositedb' 
GROUP BY state;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Security Considerations

1. **Database Credentials**: Use environment variables for database credentials
2. **Connection Encryption**: Enable SSL for production deployments
3. **Access Control**: Implement proper database user permissions
4. **Input Validation**: All spatial inputs are validated before database queries
5. **SQL Injection Prevention**: Use parameterized queries via SQLAlchemy

## Maintenance

### Regular Tasks
1. **Update Statistics**: `ANALYZE;` - Run weekly for optimal query planning
2. **Refresh Materialized Views**: Refresh when underlying data changes
3. **Monitor Index Usage**: Review pg_stat_user_indexes for unused indexes
4. **Connection Pool Monitoring**: Monitor pool utilization and adjust as needed

### Backup Strategy
1. **Full Database Backup**: Use pg_dump with --format=custom for spatial data
2. **Point-in-Time Recovery**: Configure WAL archiving for production
3. **Test Restores**: Regularly test backup restoration procedures

This comprehensive database setup ensures optimal performance for the GeoSpatial Site Readiness Analyzer's spatial analysis requirements while maintaining reliability and scalability.