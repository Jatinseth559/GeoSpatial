import json
import random
from pathlib import Path
from typing import Dict, List

import geopandas as gpd
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box

BBOX = (72.45, 22.87, 72.75, 23.15)
BBOX_POLYGON = box(*BBOX)
RNG = np.random.default_rng(42)
random.seed(42)

OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _bounded_voronoi(points: np.ndarray, bounds: Polygon) -> List[Polygon]:
    """Build bounded Voronoi polygons clipped to bounds."""
    vor = Voronoi(points)
    polygons: List[Polygon] = []
    for region_index in vor.point_region:
        region = vor.regions[region_index]
        if -1 in region or not region:
            continue
        poly = Polygon(vor.vertices[region])
        clipped = poly.intersection(bounds)
        if clipped.is_empty:
            continue
        if clipped.geom_type == "Polygon":
            polygons.append(clipped)
        elif clipped.geom_type == "MultiPolygon":
            polygons.extend([p for p in clipped.geoms if p.area > 0])
    return polygons


def create_demographics(n: int = 200) -> gpd.GeoDataFrame:
    """Create demographic zones with spatially autocorrelated income."""
    points = np.column_stack(
        [
            RNG.uniform(BBOX[0], BBOX[2], n * 3),
            RNG.uniform(BBOX[1], BBOX[3], n * 3),
        ]
    )
    raw_polys = _bounded_voronoi(points, BBOX_POLYGON)
    selected = sorted(raw_polys, key=lambda p: p.area, reverse=True)[:n]

    centroids = np.array([(p.centroid.x, p.centroid.y) for p in selected])
    base_income = RNG.uniform(15000, 150000, size=len(selected))

    smoothed_income = []
    sigma = 0.04
    for i, c in enumerate(centroids):
        distances = np.sqrt(np.sum((centroids - c) ** 2, axis=1))
        weights = np.exp(-(distances**2) / (2 * sigma**2))
        weights /= np.sum(weights)
        smoothed_income.append(float(np.dot(base_income, weights)))

    gdf = gpd.GeoDataFrame(
        {
            "zone_id": [f"DEMO_{i+1:04d}" for i in range(len(selected))],
            "name": [f"Demographic Zone {i+1}" for i in range(len(selected))],
            "population": RNG.integers(500, 50001, len(selected)),
            "median_income": smoothed_income,
            "median_age": RNG.uniform(22, 45, len(selected)),
            "youth_population_pct": RNG.uniform(25, 52, len(selected)),
            "working_age_pct": RNG.uniform(45, 72, len(selected)),
        },
        geometry=[MultiPolygon([p]) for p in selected],
        crs="EPSG:4326",
    )

    area_km2 = gdf.to_crs(3857).area / 1_000_000
    gdf["population_density"] = gdf["population"] / np.maximum(area_km2, 0.05)
    gdf["household_count"] = (gdf["population"] / RNG.uniform(2.8, 4.6, len(gdf))).astype(int)
    gdf["data_year"] = 2023
    return gdf


def generate_roads() -> gpd.GeoDataFrame:
    """Create synthetic road graph with highway/arterial/collector hierarchy."""
    roads: List[Dict] = []

    highways = [
        ((BBOX[0], 23.06), (BBOX[2], 22.96)),
        ((BBOX[0], 22.92), (BBOX[2], 23.10)),
        ((72.50, BBOX[1]), (72.66, BBOX[3])),
        ((72.57, BBOX[1]), (72.57, BBOX[3])),
        ((BBOX[0], 23.00), (BBOX[2], 23.00)),
    ]
    for i, (start, end) in enumerate(highways):
        roads.append(
            {
                "osm_id": 1_000_000 + i,
                "road_type": "motorway",
                "name": f"Highway {i+1}",
                "lanes": 4,
                "max_speed": 80,
                "is_highway": True,
                "geometry": LineString([start, end]),
            }
        )

    for i in range(20):
        start = (RNG.uniform(BBOX[0], BBOX[2]), RNG.uniform(BBOX[1], BBOX[3]))
        mid = (start[0] + RNG.uniform(-0.03, 0.03), start[1] + RNG.uniform(-0.03, 0.03))
        end = (RNG.uniform(BBOX[0], BBOX[2]), RNG.uniform(BBOX[1], BBOX[3]))
        roads.append(
            {
                "osm_id": 2_000_000 + i,
                "road_type": "primary",
                "name": f"Arterial {i+1}",
                "lanes": 3,
                "max_speed": 60,
                "is_highway": False,
                "geometry": LineString([start, mid, end]),
            }
        )

    for i in range(50):
        x = RNG.uniform(BBOX[0], BBOX[2])
        y = RNG.uniform(BBOX[1], BBOX[3])
        dx = RNG.uniform(0.01, 0.04)
        dy = RNG.uniform(-0.03, 0.03)
        roads.append(
            {
                "osm_id": 3_000_000 + i,
                "road_type": "secondary",
                "name": f"Collector {i+1}",
                "lanes": 2,
                "max_speed": 40,
                "is_highway": False,
                "geometry": LineString([(x, y), (min(BBOX[2], x + dx), min(BBOX[3], max(BBOX[1], y + dy)))]),
            }
        )

    return gpd.GeoDataFrame(roads, crs="EPSG:4326")


def _sample_cluster_points(centers: np.ndarray, n: int, spread: float = 0.015) -> np.ndarray:
    samples = []
    for _ in range(n):
        c = centers[RNG.integers(0, len(centers))]
        lng = np.clip(c[0] + RNG.normal(0, spread), BBOX[0], BBOX[2])
        lat = np.clip(c[1] + RNG.normal(0, spread), BBOX[1], BBOX[3])
        samples.append((lng, lat))
    return np.array(samples)


def generate_pois(demo_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Create POIs clustered near high-density zones."""
    dense = demo_gdf.nlargest(12, "population_density")
    centers = np.array([(g.centroid.x, g.centroid.y) for g in dense.geometry])

    categories = [
        ("retail", "competitor", 80, True, False),
        ("retail", "anchor", 100, False, True),
        ("food", "restaurant", 150, False, False),
        ("services", "service", 100, False, False),
        ("other", "business", 70, False, False),
    ]

    records: List[Dict] = []
    pid = 1
    for category, subcategory, count, is_comp, is_anchor in categories:
        pts = _sample_cluster_points(centers, count, 0.013 if is_comp or is_anchor else 0.02)
        for i, (lng, lat) in enumerate(pts):
            records.append(
                {
                    "poi_id": f"POI_{pid:05d}",
                    "name": f"{category.title()} {i+1}",
                    "category": category,
                    "subcategory": subcategory,
                    "brand": f"Brand {RNG.integers(1, 40)}",
                    "is_competitor": is_comp,
                    "is_anchor": is_anchor,
                    "rating": round(float(RNG.uniform(2.8, 4.9)), 2),
                    "review_count": int(RNG.integers(20, 2500)),
                    "geometry": Point(float(lng), float(lat)),
                }
            )
            pid += 1

    return gpd.GeoDataFrame(records, crs="EPSG:4326")


def generate_land_use(n_cols: int = 15, n_rows: int = 10) -> gpd.GeoDataFrame:
    """Generate 150 grid-like land use polygons."""
    width = (BBOX[2] - BBOX[0]) / n_cols
    height = (BBOX[3] - BBOX[1]) / n_rows
    total = n_cols * n_rows

    zone_types = (
        ["commercial"] * int(total * 0.40)
        + ["residential"] * int(total * 0.30)
        + ["industrial"] * int(total * 0.15)
        + ["mixed_use"] * int(total * 0.10)
    )
    zone_types += ["green_space"] * (total - len(zone_types))
    random.shuffle(zone_types)

    records: List[Dict] = []
    idx = 0
    for r in range(n_rows):
        for c in range(n_cols):
            minx = BBOX[0] + c * width
            miny = BBOX[1] + r * height
            maxx = minx + width
            maxy = miny + height
            zt = zone_types[idx]
            idx += 1
            records.append(
                {
                    "zone_code": f"LU_{idx:04d}",
                    "zone_type": zt,
                    "description": zt.replace("_", " ").title(),
                    "allows_retail": zt in {"commercial", "mixed_use"},
                    "allows_warehouse": zt in {"industrial", "mixed_use"},
                    "floor_area_ratio": float(RNG.uniform(0.8, 5.5) if zt != "green_space" else 0.4),
                    "max_building_height": float(RNG.uniform(8, 60) if zt != "green_space" else 4),
                    "geometry": MultiPolygon([box(minx, miny, maxx, maxy)]),
                }
            )

    return gpd.GeoDataFrame(records, crs="EPSG:4326")


def generate_environmental_risks(land_use: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Generate flood polygons, earthquake gradient, and AQI risk polygons."""
    records: List[Dict] = []
    rid = 1

    river = LineString([(72.49, 23.14), (72.54, 23.06), (72.57, 22.99), (72.61, 22.90)])
    for width, severity in [(0.01, "high"), (0.007, "moderate"), (0.005, "moderate")]:
        poly = river.buffer(width).intersection(BBOX_POLYGON)
        if poly.geom_type == "Polygon":
            poly = MultiPolygon([poly])
        records.append(
            {
                "risk_id": f"RISK_{rid:04d}",
                "risk_type": "flood",
                "severity": severity,
                "flood_zone_code": f"FZ{rid}",
                "earthquake_pga": None,
                "air_quality_index": None,
                "data_source": "Synthetic",
                "geometry": poly,
            }
        )
        rid += 1

    for x in np.linspace(BBOX[0], BBOX[2], 6):
        poly = box(x - 0.015, BBOX[1], x + 0.015, BBOX[3]).intersection(BBOX_POLYGON)
        pga = 0.08 + ((x - BBOX[0]) / (BBOX[2] - BBOX[0])) * 0.18
        records.append(
            {
                "risk_id": f"RISK_{rid:04d}",
                "risk_type": "earthquake",
                "severity": "moderate" if pga >= 0.2 else "low",
                "flood_zone_code": None,
                "earthquake_pga": round(float(pga), 4),
                "air_quality_index": None,
                "data_source": "Synthetic",
                "geometry": MultiPolygon([poly]) if poly.geom_type == "Polygon" else poly,
            }
        )
        rid += 1

    industrial = land_use[land_use["zone_type"] == "industrial"]
    for _, row in industrial.sample(min(6, len(industrial)), random_state=42).iterrows():
        centroid = row.geometry.centroid
        poly = centroid.buffer(0.018)
        records.append(
            {
                "risk_id": f"RISK_{rid:04d}",
                "risk_type": "air_quality",
                "severity": "high",
                "flood_zone_code": None,
                "earthquake_pga": None,
                "air_quality_index": round(float(RNG.uniform(145, 230)), 1),
                "data_source": "Synthetic",
                "geometry": MultiPolygon([poly]),
            }
        )
        rid += 1

    for _ in range(4):
        p = Point(RNG.uniform(BBOX[0], BBOX[2]), RNG.uniform(BBOX[1], BBOX[3]))
        records.append(
            {
                "risk_id": f"RISK_{rid:04d}",
                "risk_type": "air_quality",
                "severity": "low",
                "flood_zone_code": None,
                "earthquake_pga": None,
                "air_quality_index": round(float(RNG.uniform(45, 95)), 1),
                "data_source": "Synthetic",
                "geometry": MultiPolygon([p.buffer(0.016)]),
            }
        )
        rid += 1

    return gpd.GeoDataFrame(records, crs="EPSG:4326")


def weight_configurations() -> List[Dict]:
    """Default weight presets."""
    return [
        {
            "config_name": "Retail Store",
            "use_case": "retail",
            "weights": {
                "demographics": 0.35,
                "transport": 0.25,
                "poi": 0.20,
                "land_use": 0.10,
                "environment": 0.10,
            },
            "thresholds": {"min_population_5km": 50000, "exclude_flood_zones": True, "only_commercial": False},
            "is_default": True,
        },
        {
            "config_name": "EV Charging Station",
            "use_case": "ev_charging",
            "weights": {
                "demographics": 0.20,
                "transport": 0.40,
                "poi": 0.15,
                "land_use": 0.15,
                "environment": 0.10,
            },
            "thresholds": {"min_population_5km": 30000, "exclude_flood_zones": True, "only_commercial": False},
            "is_default": False,
        },
        {
            "config_name": "Warehouse/Logistics",
            "use_case": "warehouse",
            "weights": {
                "demographics": 0.10,
                "transport": 0.45,
                "poi": 0.10,
                "land_use": 0.25,
                "environment": 0.10,
            },
            "thresholds": {"min_population_5km": 10000, "exclude_flood_zones": True, "only_commercial": False},
            "is_default": False,
        },
        {
            "config_name": "Telecom Tower",
            "use_case": "telecom",
            "weights": {
                "demographics": 0.30,
                "transport": 0.15,
                "poi": 0.05,
                "land_use": 0.30,
                "environment": 0.20,
            },
            "thresholds": {"min_population_5km": 20000, "exclude_flood_zones": False, "only_commercial": False},
            "is_default": False,
        },
    ]


def export_all() -> None:
    """Generate all synthetic layers and export to GeoJSON/JSON."""
    demographics = create_demographics(200)
    roads = generate_roads()
    pois = generate_pois(demographics)
    land_use = generate_land_use()
    env = generate_environmental_risks(land_use)

    demographics.to_file(OUTPUT_DIR / "demographics.geojson", driver="GeoJSON")
    roads.to_file(OUTPUT_DIR / "roads.geojson", driver="GeoJSON")
    pois.to_file(OUTPUT_DIR / "pois.geojson", driver="GeoJSON")
    land_use.to_file(OUTPUT_DIR / "land_use.geojson", driver="GeoJSON")
    env.to_file(OUTPUT_DIR / "environmental_risks.geojson", driver="GeoJSON")

    with open(OUTPUT_DIR / "weight_configs.json", "w", encoding="utf-8") as f:
        json.dump(weight_configurations(), f, indent=2)

    print("\033[92m? Synthetic data generated in backend/data_pipeline/data\033[0m")


def main() -> None:
    export_all()


if __name__ == "__main__":
    main()
