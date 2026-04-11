from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy import text
from core.database import engine
from core.schemas import SaveSiteRequest, CandidateSiteResponse
from services.scoring_engine import scoring_engine
from services.isochrone_service import isochrone_service
import json

router = APIRouter(prefix="/api/v1/sites", tags=["sites"])


@router.post("/save")
async def save_site(request: SaveSiteRequest):
    score_result = await scoring_engine.compute_score(
        lat=request.lat,
        lng=request.lng,
        weights=request.weights,
        use_case=request.use_case
    )
    
    isochrone_result = await isochrone_service.get_isochrones(
        lat=request.lat,
        lng=request.lng,
        modes=["drive"],
        minutes_list=[10, 20, 30]
    )
    
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            INSERT INTO candidate_sites 
            (site_name, description, geom, latitude, longitude, 
             composite_score, score_breakdown, weights_used,
             catchment_pop_10min, catchment_pop_20min, catchment_pop_30min)
            VALUES (:name, :desc, ST_SetSRID(ST_Point(:lng, :lat), 4326),
                    :lat, :lng, :score, :breakdown, :weights,
                    :pop_10, :pop_20, :pop_30)
            RETURNING id
        """), {
            "name": request.name,
            "desc": request.description,
            "lat": request.lat,
            "lng": request.lng,
            "score": score_result["composite_score"],
            "breakdown": json.dumps(score_result["sub_scores"]),
            "weights": json.dumps(request.weights) if request.weights else None,
            "pop_10": isochrone_result["catchment_population"].get("drive_10min", 0),
            "pop_20": isochrone_result["catchment_population"].get("drive_20min", 0),
            "pop_30": isochrone_result["catchment_population"].get("drive_30min", 0),
        })
        
        site_id = result.scalar()
    
    return {"id": site_id, "message": "Site saved successfully"}


@router.get("/")
async def get_sites():
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT id, site_name, description, latitude, longitude,
                   composite_score, score_breakdown, weights_used,
                   catchment_pop_10min, catchment_pop_20min, catchment_pop_30min,
                   created_at
            FROM candidate_sites
            ORDER BY created_at DESC
        """))
        
        rows = result.fetchall()
        
        sites = []
        for row in rows:
            sites.append({
                "id": row[0],
                "site_name": row[1],
                "description": row[2],
                "latitude": row[3],
                "longitude": row[4],
                "composite_score": row[5],
                "score_breakdown": json.loads(row[6]) if row[6] else None,
                "weights_used": json.loads(row[7]) if row[7] else None,
                "catchment_pop_10min": row[8],
                "catchment_pop_20min": row[9],
                "catchment_pop_30min": row[10],
                "created_at": row[11].isoformat() if row[11] else None
            })
        
        return sites


@router.get("/{site_id}")
async def get_site(site_id: int):
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT id, site_name, description, latitude, longitude,
                   composite_score, score_breakdown, weights_used,
                   catchment_pop_10min, catchment_pop_20min, catchment_pop_30min,
                   created_at
            FROM candidate_sites
            WHERE id = :id
        """), {"id": site_id})
        
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Site not found")
        
        return {
            "id": row[0],
            "site_name": row[1],
            "description": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "composite_score": row[5],
            "score_breakdown": json.loads(row[6]) if row[6] else None,
            "weights_used": json.loads(row[7]) if row[7] else None,
            "catchment_pop_10min": row[8],
            "catchment_pop_20min": row[9],
            "catchment_pop_30min": row[10],
            "created_at": row[11].isoformat() if row[11] else None
        }


@router.post("/compare")
async def compare_sites(site_ids: List[int]):
    if len(site_ids) < 2 or len(site_ids) > 4:
        raise HTTPException(status_code=400, detail="Select 2-4 sites for comparison")
    
    async with engine.begin() as conn:
        placeholders = ",".join([str(id) for id in site_ids])
        result = await conn.execute(text(f"""
            SELECT id, site_name, latitude, longitude, composite_score,
                   score_breakdown, catchment_pop_10min, catchment_pop_20min, catchment_pop_30min
            FROM candidate_sites
            WHERE id IN ({placeholders})
        """))
        
        rows = result.fetchall()
        
        sites = []
        for row in rows:
            breakdown = json.loads(row[5]) if row[5] else {}
            sites.append({
                "id": row[0],
                "site_name": row[1],
                "lat": row[2],
                "lng": row[3],
                "composite_score": row[4],
                "sub_scores": breakdown,
                "catchment": {
                    "10min": row[6],
                    "20min": row[7],
                    "30min": row[8]
                }
            })
        
        rankings = {
            "composite": [],
            "demographics": [],
            "transport": [],
            "poi": [],
            "land_use": [],
            "environment": [],
            "catchment": []
        }
        
        for site in sites:
            rankings["composite"].append(site["id"])
            for key in ["demographics", "transport", "poi", "land_use", "environment"]:
                rankings[key].append(site["id"])
            total_pop = (site["catchment"]["10min"] or 0) + (site["catchment"]["20min"] or 0) + (site["catchment"]["30min"] or 0)
            rankings["catchment"].append((site["id"], total_pop))
        
        rankings["composite"] = sorted(rankings["composite"], 
            key=lambda x: next(s["composite_score"] for s in sites if s["id"] == x), reverse=True)
        
        for key in ["demographics", "transport", "poi", "land_use", "environment"]:
            rankings[key] = sorted(rankings[key],
                key=lambda x: next(s["sub_scores"].get(key, 0) for s in sites if s["id"] == x), reverse=True)
        
        rankings["catchment"] = sorted(rankings["catchment"], key=lambda x: x[1], reverse=True)
        
        return {"sites": sites, "rankings": rankings}