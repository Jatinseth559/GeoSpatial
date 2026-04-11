"""
Simple H3-compatible hex grid implementation without native dependency.
Uses approximate hexagonal binning based on lat/lng.
"""

import math
from typing import List, Tuple, Dict, Any

def geo_to_h3(lat: float, lng: float, resolution: int) -> str:
    """Convert lat/lng to H3 index string (simplified approximation)."""
    base = 1000000 + resolution
    lat_idx = int((lat + 90) * 10000)
    lng_idx = int((lng + 180) * 10000)
    return f"{base}{lat_idx:08d}{lng_idx:08d}"

def h3_to_geo(h3_index: str) -> Tuple[float, float]:
    """Convert H3 index to lat/lng center (simplified)."""
    resolution = int(h3_index[0]) - 1
    lat_idx = int(h3_index[1:9])
    lng_idx = int(h3_index[9:17])
    lat = lat_idx / 10000 - 90
    lng = lng_idx / 10000 - 180
    return (lat, lng)

def h3_to_geo_boundary(h3_index: str) -> List[Tuple[float, float]]:
    """Get hex boundary coordinates."""
    center_lat, center_lng = h3_to_geo(h3_index)
    resolution = int(h3_index[0]) - 1
    radius = 0.01 / (resolution + 1)
    
    coords = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        lat = center_lat + radius * math.cos(angle)
        lng = center_lng + radius * math.sin(angle) / math.cos(math.radians(center_lat))
        coords.append((lat, lng))
    return coords

def k_ring(h3_index: str, k: int) -> List[str]:
    """Get k-ring of hexagons around the center."""
    center_lat, center_lng = h3_to_geo(h3_index)
    resolution = int(h3_index[0]) - 1
    radius = 0.01 / (resolution + 1) * k
    
    hexes = [h3_index]
    for lat_offset in range(-k, k + 1):
        for lng_offset in range(-k, k + 1):
            if lat_offset == 0 and lng_offset == 0:
                continue
            lat = center_lat + lat_offset * radius
            lng = center_lng + lng_offset * radius * math.cos(math.radians(center_lat))
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                hexes.append(geo_to_h3(lat, lng, resolution))
    return hexes

def polyfill(polygon: Dict[str, Any], resolution: int, geo_json_conformant: bool = True) -> List[str]:
    """Fill polygon with H3 hexagons at given resolution."""
    # Extract coordinates from GeoJSON polygon
    if 'coordinates' in polygon:
        coords = polygon['coordinates'][0]  # Exterior ring
    else:
        coords = polygon
    
    # Find bounding box
    lats = [coord[1] for coord in coords]
    lngs = [coord[0] for coord in coords]
    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)
    
    # Generate hex grid within bounding box
    hexes = []
    step = 0.01 / (resolution + 1)  # Approximate hex size
    
    lat = min_lat
    while lat <= max_lat:
        lng = min_lng
        while lng <= max_lng:
            # Simple point-in-polygon check (simplified)
            if _point_in_polygon(lat, lng, coords):
                hex_id = geo_to_h3(lat, lng, resolution)
                hexes.append(hex_id)
            lng += step
        lat += step
    
    return hexes

def _point_in_polygon(lat: float, lng: float, coords: List[Tuple[float, float]]) -> bool:
    """Simple point-in-polygon test using ray casting."""
    x, y = lng, lat
    n = len(coords)
    inside = False
    
    p1x, p1y = coords[0]
    for i in range(1, n + 1):
        p2x, p2y = coords[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside