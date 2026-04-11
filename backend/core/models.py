from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Numeric, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from core.database import Base


class DemographicZone(Base):
    __tablename__ = "demographic_zones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200))
    # Store geometry as WKT text for SQLite compatibility
    geom_wkt = Column(Text, nullable=False)
    population = Column(Integer)
    population_density = Column(Float)
    median_income = Column(Float)
    median_age = Column(Float)
    youth_population_pct = Column(Float)
    working_age_pct = Column(Float)
    household_count = Column(Integer)
    data_year = Column(Integer, default=2023)
    created_at = Column(DateTime, server_default=func.now())


class RoadNetwork(Base):
    __tablename__ = "road_network"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    osm_id = Column(Numeric(20))
    road_type = Column(String(50))
    name = Column(String(200))
    geom_wkt = Column(Text, nullable=False)
    lanes = Column(Integer)
    max_speed = Column(Integer)
    is_highway = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class PointsOfInterest(Base):
    __tablename__ = "points_of_interest"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(String(100), unique=True)
    name = Column(String(300))
    category = Column(String(100))
    subcategory = Column(String(100))
    geom_wkt = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    brand = Column(String(200))
    is_competitor = Column(Boolean, default=False)
    is_anchor = Column(Boolean, default=False)
    rating = Column(Float)
    review_count = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


class LandUseZone(Base):
    __tablename__ = "land_use_zones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_code = Column(String(50))
    zone_type = Column(String(100))
    description = Column(Text)
    geom_wkt = Column(Text, nullable=False)
    allows_retail = Column(Boolean, default=False)
    allows_warehouse = Column(Boolean, default=False)
    floor_area_ratio = Column(Float)
    max_building_height = Column(Float)
    created_at = Column(DateTime, server_default=func.now())


class EnvironmentalRisk(Base):
    __tablename__ = "environmental_risks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    risk_id = Column(String(100))
    risk_type = Column(String(100))
    severity = Column(String(50))
    geom_wkt = Column(Text, nullable=False)
    flood_zone_code = Column(String(20))
    earthquake_pga = Column(Float)
    air_quality_index = Column(Float)
    data_source = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())


class CandidateSite(Base):
    __tablename__ = "candidate_sites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_name = Column(String(300))
    description = Column(Text)
    geom_wkt = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    composite_score = Column(Float)
    score_breakdown = Column(JSON)
    weights_used = Column(JSON)
    isochrone_10min_wkt = Column(Text)
    isochrone_20min_wkt = Column(Text)
    isochrone_30min_wkt = Column(Text)
    catchment_pop_10min = Column(Integer)
    catchment_pop_20min = Column(Integer)
    catchment_pop_30min = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class H3HexScore(Base):
    __tablename__ = "h3_hex_scores"
    
    h3_index = Column(String(20), primary_key=True)
    h3_resolution = Column(Integer, default=8)
    center_lat = Column(Float)
    center_lng = Column(Float)
    composite_score = Column(Float)
    score_breakdown = Column(JSON)
    is_hotspot = Column(Boolean, default=False)
    is_coldspot = Column(Boolean, default=False)
    gi_star_value = Column(Float)
    cluster_label = Column(Integer)
    population_in_hex = Column(Integer)
    computed_at = Column(DateTime, server_default=func.now())


class WeightConfiguration(Base):
    __tablename__ = "weight_configurations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_name = Column(String(200), unique=True, nullable=False)
    use_case = Column(String(100))
    weights = Column(JSON, nullable=False)
    thresholds = Column(JSON)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())