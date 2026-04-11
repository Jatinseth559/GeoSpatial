from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from core.schemas import GeoJSONFeatureCollection
from services.layer_processor import layer_processor

router = APIRouter(prefix="/api/v1/layers", tags=["layers"])


@router.get("/demographics", response_model=GeoJSONFeatureCollection)
async def get_demographics():
    return await layer_processor.get_demographics_layer()


@router.get("/roads", response_model=GeoJSONFeatureCollection)
async def get_roads():
    return await layer_processor.get_roads_layer()


@router.get("/poi", response_model=GeoJSONFeatureCollection)
async def get_poi(category: Optional[str] = Query(None)):
    return await layer_processor.get_poi_layer(category)


@router.get("/land-use", response_model=GeoJSONFeatureCollection)
async def get_land_use():
    return await layer_processor.get_land_use_layer()


@router.get("/environment", response_model=GeoJSONFeatureCollection)
async def get_environment():
    return await layer_processor.get_environmental_layer()