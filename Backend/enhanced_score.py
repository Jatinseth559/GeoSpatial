from fastapi import APIRouter
from pydantic import BaseModel
from services.geospatial_analyzer import geospatial_analyzer

router = APIRouter(prefix="/api/v1/enhanced", tags=["enhanced-scoring"])


class EnhancedScoreRequest(BaseModel):
    lat: float
    lng: float
    use_case: str = "retail"


@router.post("/score")
async def get_enhanced_score(request: EnhancedScoreRequest):
    """
    Get comprehensive geospatial site readiness analysis.
    
    Provides detailed analysis across 5 key dimensions:
    - Demographics: Population, income, age distribution
    - Transport: Highway access, airport/railway connectivity  
    - Infrastructure: Power, water, internet, waste management
    - Market Potential: Competition analysis, market opportunity
    - Environmental: Flood risk, air quality, safety factors
    
    Supports multiple use cases: retail, office, warehouse, restaurant, residential, industrial
    """
    result = await geospatial_analyzer.analyze_site(
        lat=request.lat,
        lng=request.lng,
        use_case=request.use_case
    )
    return result
