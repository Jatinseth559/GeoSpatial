from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from core.schemas import (
    PointScoreRequest, ScoreResponse, BatchScoreRequest,
    IsochroneRequest, IsochroneResponse
)
from services.scoring_engine import scoring_engine
from services.isochrone_service import isochrone_service
from core.database import get_db
import json

router = APIRouter(prefix="/api/v1/score", tags=["scoring"])


@router.post("/point", response_model=ScoreResponse)
async def score_point(request: PointScoreRequest):
    result = await scoring_engine.score_location(
        lat=request.lat,
        lng=request.lng,
        weights=request.weights,
        use_case=request.use_case
    )
    return result


@router.post("/batch", response_model=List[ScoreResponse])
async def score_batch(request: BatchScoreRequest):
    if len(request.points) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 points per request")
    
    results = []
    for point in request.points:
        result = await scoring_engine.score_location(
            lat=point["lat"],
            lng=point["lng"],
            weights=request.weights,
            use_case=request.use_case
        )
        results.append(result)
    
    return results


@router.get("/hex-grid")
async def get_hex_grid(resolution: int = 8, use_case: Optional[str] = None):
    from services.clustering_service import clustering_service
    
    weights = None
    if use_case:
        from core.database import engine
        async with engine.begin() as conn:
            result = await conn.execute(
                f"SELECT weights FROM weight_configurations WHERE use_case = '{use_case}'"
            )
            row = result.fetchone()
            if row:
                weights = json.loads(row[0])
    
    geojson = await clustering_service.get_hex_grid_geojson(
        resolution=resolution,
        weights=weights,
        use_case=use_case
    )
    return geojson


@router.post("/isochrone", response_model=IsochroneResponse)
async def compute_isochrone(request: IsochroneRequest):
    result = await isochrone_service.get_isochrones(
        lat=request.lat,
        lng=request.lng,
        modes=request.modes,
        minutes_list=request.minutes
    )
    return result