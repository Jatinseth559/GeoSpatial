"""
Database enhancements for SQLite optimization.

This module provides SQLite-compatible database setup functions.
"""

import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def create_additional_indexes(engine: AsyncEngine) -> None:
    """Create additional indexes for optimal performance."""
    
    additional_indexes = [
        # Composite indexes for common query patterns
        "CREATE INDEX IF NOT EXISTS idx_demographic_zones_density_income ON demographic_zones (population_density, median_income)",
        "CREATE INDEX IF NOT EXISTS idx_poi_category_competitor ON points_of_interest (category, is_competitor)",
        "CREATE INDEX IF NOT EXISTS idx_poi_category_anchor ON points_of_interest (category, is_anchor)",
        "CREATE INDEX IF NOT EXISTS idx_road_network_type_highway ON road_network (road_type, is_highway)",
        "CREATE INDEX IF NOT EXISTS idx_land_use_retail_warehouse ON land_use_zones (allows_retail, allows_warehouse)",
        "CREATE INDEX IF NOT EXISTS idx_env_risk_type_severity ON environmental_risks (risk_type, severity)",
        
        # Performance indexes for scoring queries
        "CREATE INDEX IF NOT EXISTS idx_h3_hex_scores_resolution_score ON h3_hex_scores (h3_resolution, composite_score)",
        "CREATE INDEX IF NOT EXISTS idx_h3_hex_scores_hotspot_resolution ON h3_hex_scores (is_hotspot, h3_resolution)",
        "CREATE INDEX IF NOT EXISTS idx_candidate_sites_score_desc ON candidate_sites (composite_score DESC)",
        
        # Coordinate indexes for spatial queries
        "CREATE INDEX IF NOT EXISTS idx_poi_lat_lng ON points_of_interest (latitude, longitude)",
        "CREATE INDEX IF NOT EXISTS idx_candidate_sites_lat_lng ON candidate_sites (latitude, longitude)",
    ]
    
    async with engine.begin() as conn:
        for index_sql in additional_indexes:
            try:
                await conn.execute(text(index_sql))
                logger.info(f"Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")


async def optimize_sqlite_settings(engine: AsyncEngine) -> None:
    """Apply SQLite optimization settings."""
    
    optimization_settings = [
        # SQLite performance optimizations
        "PRAGMA journal_mode = WAL",
        "PRAGMA synchronous = NORMAL", 
        "PRAGMA cache_size = 10000",
        "PRAGMA temp_store = MEMORY",
        "PRAGMA mmap_size = 268435456",  # 256MB
    ]
    
    async with engine.begin() as conn:
        for setting in optimization_settings:
            try:
                await conn.execute(text(setting))
                logger.info(f"Applied setting: {setting}")
            except Exception as e:
                logger.warning(f"Failed to apply setting {setting}: {e}")


async def verify_indexes(engine: AsyncEngine) -> dict:
    """Verify that indexes exist."""
    
    index_check_query = """
    SELECT name FROM sqlite_master 
    WHERE type = 'index' 
    AND name LIKE 'idx_%'
    ORDER BY name;
    """
    
    async with engine.begin() as conn:
        result = await conn.execute(text(index_check_query))
        indexes = result.fetchall()
        
        index_info = {
            'total_indexes': len(indexes),
            'index_names': [row[0] for row in indexes]
        }
        
        logger.info(f"Found {len(indexes)} custom indexes")
        
        return index_info


async def enhance_database_setup(engine: AsyncEngine) -> dict:
    """
    Comprehensive database enhancement setup for SQLite.
    
    Returns:
        dict: Summary of enhancements applied
    """
    
    enhancements = {
        'indexes': False,
        'optimization_settings': False,
        'index_verification': {},
        'errors': []
    }
    
    try:
        logger.info("Starting SQLite database enhancements...")
        
        # Create additional indexes
        await create_additional_indexes(engine)
        enhancements['indexes'] = True
        
        # Apply SQLite optimizations
        await optimize_sqlite_settings(engine)
        enhancements['optimization_settings'] = True
        
        # Verify indexes
        enhancements['index_verification'] = await verify_indexes(engine)
        
        logger.info("SQLite database enhancements completed successfully")
        
    except Exception as e:
        error_msg = f"Database enhancement failed: {e}"
        logger.error(error_msg)
        enhancements['errors'].append(error_msg)
    
    return enhancements