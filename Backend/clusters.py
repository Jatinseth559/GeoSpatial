from fastapi import APIRouter, Query
from typing import Optional, List
from services.clustering_service import clustering_service

router = APIRouter(prefix="/api/v1/clusters", tags=["clusters"])


@router.get("/hotspots")
async def get_hotspots(
    resolution: int = Query(8, ge=7, le=9),
    use_case: Optional[str] = None
):
    weights = None
    if use_case:
        from core.database import engine
        import json
        async with engine.begin() as conn:
            result = await conn.execute(
                f"SELECT weights FROM weight_configurations WHERE use_case = '{use_case}'"
            )
            row = result.fetchone()
            if row:
                weights = json.loads(row[0])
    
    hex_scores = await clustering_service.compute_hex_grid_scores(
        resolution=resolution,
        weights=weights,
        use_case=use_case
    )
    
    clustered = await clustering_service.run_dbscan_clustering(hex_scores)
    
    results = await clustering_service.compute_getis_ord(clustered)
    
    features = []
    for hex_data in results:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [hex_data["center_lng"], hex_data["center_lat"]]
            },
            "properties": {
                "h3_index": hex_data["h3_index"],
                "composite_score": hex_data["composite_score"],
                "gi_star_value": hex_data.get("gi_star_value", 0),
                "is_hotspot": hex_data.get("is_hotspot", False),
                "is_coldspot": hex_data.get("is_coldspot", False),
                "cluster_label": hex_data.get("cluster_label", -1)
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/hex-grid")
async def get_hex_grid_geojson(resolution: int = Query(8, ge=7, le=9)):
    return await clustering_service.get_hex_grid_geojson(resolution=resolution)