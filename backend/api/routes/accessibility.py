from fastapi import APIRouter, HTTPException
from core.schemas import IsochroneRequest, IsochroneResponse
from services.isochrone_service import isochrone_service

router = APIRouter(prefix="/api/v1/accessibility", tags=["accessibility"])


@router.post("/isochrone", response_model=IsochroneResponse)
async def compute_isochrone(request: IsochroneRequest):
    if not request.modes:
        raise HTTPException(status_code=400, detail="At least one mode is required")
    
    if not request.minutes:
        raise HTTPException(status_code=400, detail="At least one time in minutes is required")
    
    result = await isochrone_service.get_isochrones(
        lat=request.lat,
        lng=request.lng,
        modes=request.modes,
        minutes_list=request.minutes
    )
    return result