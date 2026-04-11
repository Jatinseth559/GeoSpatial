from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScoreRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    weights: Optional[Dict[str, float]] = None
    use_case: Optional[str] = None


class PointScoreRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    weights: Optional[Dict[str, float]] = None
    use_case: Optional[str] = None


class BatchScoreRequest(BaseModel):
    points: List[Dict[str, float]]
    weights: Optional[Dict[str, float]] = None
    use_case: Optional[str] = None


class SubScoreExplanation(BaseModel):
    demographics: Optional[str] = None
    transport: Optional[str] = None
    poi: Optional[str] = None
    land_use: Optional[str] = None
    environment: Optional[str] = None


class ScoreResponse(BaseModel):
    composite_score: float
    layer_scores: Dict[str, float]
    layer_details: Optional[Dict[str, Any]] = None
    weights_used: Dict[str, float]
    use_case: Optional[str] = None
    location: Dict[str, float]
    
    # Legacy fields for backward compatibility
    sub_scores: Optional[Dict[str, float]] = None
    explanations: Optional[SubScoreExplanation] = None
    threshold_violations: List[str] = []
    lat: Optional[float] = None
    lng: Optional[float] = None
    
    def __init__(self, **data):
        # Map layer_scores to sub_scores for backward compatibility
        if 'layer_scores' in data and 'sub_scores' not in data:
            data['sub_scores'] = data['layer_scores']
        
        # Extract lat/lng from location if present
        if 'location' in data:
            if 'lat' not in data:
                data['lat'] = data['location'].get('latitude')
            if 'lng' not in data:
                data['lng'] = data['location'].get('longitude')
        
        super().__init__(**data)


class HexGridRequest(BaseModel):
    resolution: int = Field(8, ge=7, le=9)
    use_case: Optional[str] = None
    weights: Optional[Dict[str, float]] = None


class IsochroneRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    modes: List[str] = Field(default=["drive"])
    minutes: List[int] = Field(default=[10, 20, 30])


class IsochroneResponse(BaseModel):
    isochrones: List[Dict[str, Any]]
    catchment_population: Dict[str, int]


class SaveSiteRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    name: str
    description: Optional[str] = None
    use_case: Optional[str] = None
    weights: Optional[Dict[str, float]] = None


class CandidateSiteResponse(BaseModel):
    id: int
    site_name: Optional[str]
    description: Optional[str]
    latitude: float
    longitude: float
    composite_score: Optional[float]
    score_breakdown: Optional[Dict[str, Any]]
    weights_used: Optional[Dict[str, Any]]
    catchment_pop_10min: Optional[int]
    catchment_pop_20min: Optional[int]
    catchment_pop_30min: Optional[int]
    created_at: datetime


class CompareSitesRequest(BaseModel):
    site_ids: List[int] = Field(..., min_items=2, max_items=4)


class CompareSitesResponse(BaseModel):
    sites: List[Dict[str, Any]]
    rankings: Dict[str, int]


class WeightConfigResponse(BaseModel):
    id: int
    config_name: str
    use_case: Optional[str]
    weights: Dict[str, float]
    thresholds: Optional[Dict[str, Any]]
    is_default: bool


class WebSocketMessage(BaseModel):
    action: str
    resolution: Optional[int] = None
    use_case: Optional[str] = None
    weights: Optional[Dict[str, float]] = None


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]