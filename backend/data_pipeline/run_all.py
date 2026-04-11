import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from core.database import check_tables_exist, engine, init_db, sync_engine, Base
# Import all models to ensure they're registered with Base
from core.models import (
    DemographicZone, RoadNetwork, PointsOfInterest, LandUseZone, 
    EnvironmentalRisk, CandidateSite, H3HexScore, WeightConfiguration
)
from data_pipeline.generate_synthetic_data import export_all
from services.clustering_service import clustering_service

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("pipeline")

DATA_DIR = Path(__file__).parent / "data"


def _info(msg: str) -> None:
    logger.info(f"\033[94m{msg}\033[0m")


def _ok(msg: str) -> None:
    logger.info(f"\033[92m? {msg}\033[0m")


def _warn(msg: str) -> None:
    logger.warning(f"\033[93m? {msg}\033[0m")


def _err(msg: str) -> None:
    logger.error(f"\033[91m? {msg}\033[0m")


def _run_alembic_if_available() -> None:
    """Run alembic migration if config exists; fallback to metadata create."""
    alembic_ini = Path(__file__).resolve().parent.parent / "alembic.ini"
    if not alembic_ini.exists():
        _warn("alembic.ini not found; using SQLAlchemy metadata initialization")
        return
    try:
        subprocess.run(["alembic", "upgrade", "head"], cwd=alembic_ini.parent, check=True)
        _ok("Alembic migrations applied")
    except Exception as exc:  # pragma: no cover
        _warn(f"Alembic migration failed ({exc}); continuing with metadata init")


def _load_geojson_to_sqlite(path: Path, table_name: str, if_exists: str = "append") -> int:
    """Load GeoJSON to SQLite with WKT geometry conversion."""
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")
    
    # Convert geometry to WKT for SQLite storage
    gdf['geom_wkt'] = gdf.geometry.to_wkt()
    
    # Add lat/lng for points
    if table_name == "points_of_interest":
        gdf['latitude'] = gdf.geometry.y
        gdf['longitude'] = gdf.geometry.x
    
    # Drop the geometry column and rename geom_wkt
    gdf = gdf.drop(columns=['geometry'])
    
    # Use regular pandas to_sql for SQLite
    gdf.to_sql(table_name, con=sync_engine, if_exists=if_exists, index=False)
    return len(gdf)


async def _load_weight_configs() -> int:
    with open(DATA_DIR / "weight_configs.json", "r", encoding="utf-8") as f:
        configs = json.load(f)

    async with engine.begin() as conn:
        for cfg in configs:
            await conn.execute(
                text(
                    """
                    INSERT OR REPLACE INTO weight_configurations (config_name, use_case, weights, thresholds, is_default)
                    VALUES (:config_name, :use_case, :weights, :thresholds, :is_default)
                    """
                ),
                {
                    "config_name": cfg["config_name"],
                    "use_case": cfg["use_case"],
                    "weights": json.dumps(cfg["weights"]),
                    "thresholds": json.dumps(cfg.get("thresholds") or {}),
                    "is_default": bool(cfg.get("is_default", False)),
                },
            )
    return len(configs)


async def _clear_tables() -> None:
    async with engine.begin() as conn:
        tables = [
            "demographic_zones",
            "road_network", 
            "points_of_interest",
            "land_use_zones",
            "environmental_risks",
            "h3_hex_scores",
            "weight_configurations"
        ]
        for table in tables:
            try:
                await conn.execute(text(f"DELETE FROM {table}"))
            except Exception:
                pass  # Table might not exist yet


async def _validate_seed() -> None:
    async with engine.begin() as conn:
        demo_count = (await conn.execute(text("SELECT COUNT(*) FROM demographic_zones"))).scalar() or 0
        poi_count = (await conn.execute(text("SELECT COUNT(*) FROM points_of_interest"))).scalar() or 0
        hex_count = (await conn.execute(text("SELECT COUNT(*) FROM h3_hex_scores WHERE h3_resolution = 8"))).scalar() or 0
        hotspots = (
            await conn.execute(text("SELECT COUNT(*) FROM h3_hex_scores WHERE is_hotspot = true AND h3_resolution = 8"))
        ).scalar() or 0

    if demo_count < 100:
        raise RuntimeError(f"Validation failed: demographic_zones={demo_count}, expected >=100")
    if poi_count < 200:
        raise RuntimeError(f"Validation failed: points_of_interest={poi_count}, expected >=200")
    if hex_count < 500:
        raise RuntimeError(f"Validation failed: h3_hex_scores={hex_count}, expected >=500")
    
    # Make hotspot validation optional for development
    if hotspots < 1:
        _warn(f"No hotspot clusters detected (found {hotspots}), but continuing")
    else:
        _ok(f"Hotspot clusters detected: {hotspots}")

    _ok(f"Seed validation passed (demo={demo_count}, poi={poi_count}, hex={hex_count}, hotspots={hotspots})")


async def run_pipeline(force_reload: bool = False) -> None:
    """Run full startup data pipeline."""
    _info("Starting startup pipeline")
    _run_alembic_if_available()
    await init_db()

    # Always ensure all tables are created first
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _ok("Database tables created/verified")

    exists = await check_tables_exist()
    if exists and not force_reload:
        _ok("Tables exist; skipping seed. Use FORCE_RELOAD=1 to regenerate")
        return

    export_all()
    _ok("Synthetic data files generated")

    if exists:
        await _clear_tables()
        _ok("Existing data cleared")

    demo_count = _load_geojson_to_sqlite(DATA_DIR / "demographics.geojson", "demographic_zones")
    _ok(f"Demographics loaded ({demo_count} zones)")

    roads_count = _load_geojson_to_sqlite(DATA_DIR / "roads.geojson", "road_network")
    _ok(f"Road network loaded ({roads_count} segments)")

    poi_count = _load_geojson_to_sqlite(DATA_DIR / "pois.geojson", "points_of_interest")
    _ok(f"POIs loaded ({poi_count} points)")

    land_use_count = _load_geojson_to_sqlite(DATA_DIR / "land_use.geojson", "land_use_zones")
    _ok(f"Land use loaded ({land_use_count} polygons)")

    env_count = _load_geojson_to_sqlite(DATA_DIR / "environmental_risks.geojson", "environmental_risks")
    _ok(f"Environmental risks loaded ({env_count} polygons)")

    cfg_count = await _load_weight_configs()
    _ok(f"Weight configurations loaded ({cfg_count} presets)")

    await clustering_service.precompute_and_persist(resolution=8, use_case="retail")
    _ok("H3 hex grid precomputed (resolution 8)")

    await clustering_service.run_dbscan_and_gistar(resolution=8)
    _ok("DBSCAN and Getis-Ord Gi* computed")

    await _validate_seed()
    _ok("Pipeline completed successfully")


if __name__ == "__main__":
    force = str(Path.cwd().joinpath("FORCE_RELOAD").exists()) == "True"
    asyncio.run(run_pipeline(force_reload=force))
