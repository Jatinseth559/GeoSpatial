import json
import math
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
from sklearn.cluster import DBSCAN
from sqlalchemy import text

from config import settings
from core.database import engine

try:
    import h3
except Exception:  # pragma: no cover
    from core import h3_compat as h3


def _hex_worker(args: tuple[str, Dict[str, float]]) -> Dict[str, Any]:
    """CPU worker for scoring one hex index."""
    h3_index, weights = args
    lat, lng = h3.h3_to_geo(h3_index)

    center_lat, center_lng = 23.0225, 72.5714
    dist = math.sqrt((lat - center_lat) ** 2 + (lng - center_lng) ** 2)

    demographics = max(0.0, min(100.0, 95 - dist * 420 + (lat - 23.0) * 55))
    transport = max(0.0, min(100.0, 92 - abs(lng - center_lng) * 350 + (lat - 22.95) * 35))
    poi = max(0.0, min(100.0, 88 - dist * 390 + (center_lng - lng) * 60))
    land_use = max(0.0, min(100.0, 82 - abs(lat - 23.03) * 260 + (lng - 72.53) * 75))
    environment = max(0.0, min(100.0, 90 - abs(lat - 22.94) * 240 - abs(lng - 72.65) * 180))

    composite = (
        weights.get("demographics", 0.35) * demographics
        + weights.get("transport", 0.25) * transport
        + weights.get("poi", 0.20) * poi
        + weights.get("land_use", 0.10) * land_use
        + weights.get("environment", 0.10) * environment
    )

    return {
        "h3_index": h3_index,
        "center_lat": float(lat),
        "center_lng": float(lng),
        "composite_score": float(max(0, min(100, composite))),
        "score_breakdown": {
            "demographics": round(demographics, 2),
            "transport": round(transport, 2),
            "poi": round(poi, 2),
            "land_use": round(land_use, 2),
            "environment": round(environment, 2),
        },
    }


class ClusteringService:
    """Hex generation, DBSCAN clustering, and Gi* hotspot analysis."""

    @staticmethod
    def _normalize_weights(weights: Optional[Dict[str, float]]) -> Dict[str, float]:
        w = weights or {
            "demographics": 0.35,
            "transport": 0.25,
            "poi": 0.20,
            "land_use": 0.10,
            "environment": 0.10,
        }
        total = sum(w.values()) or 1
        return {k: float(v) / total for k, v in w.items()}

    @staticmethod
    def _hexes_for_bbox(resolution: int) -> List[str]:
        min_lng, min_lat, max_lng, max_lat = settings.bbox
        polygon = {
            "type": "Polygon",
            "coordinates": [
                [
                    [min_lng, min_lat],
                    [max_lng, min_lat],
                    [max_lng, max_lat],
                    [min_lng, max_lat],
                    [min_lng, min_lat],
                ]
            ],
        }
        try:
            hexes = h3.polyfill(polygon, resolution, geo_json_conformant=True)
        except TypeError:
            # fallback for compat wrapper
            center_hex = h3.geo_to_h3((min_lat + max_lat) / 2, (min_lng + max_lng) / 2, resolution)
            hexes = set(h3.k_ring(center_hex, 65))
        return sorted(list(hexes))

    async def precompute_and_persist(
        self,
        resolution: int = 8,
        use_case: Optional[str] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, Any]]:
        """Compute all study-area hex scores using multiprocessing and persist."""
        weights = self._normalize_weights(weights)
        hex_ids = self._hexes_for_bbox(resolution)

        with ProcessPoolExecutor() as pool:
            scores = list(pool.map(_hex_worker, [(hid, weights) for hid in hex_ids]))

        async with engine.begin() as conn:
            for score in scores:
                await conn.execute(
                    text(
                        """
                        INSERT OR REPLACE INTO h3_hex_scores
                            (h3_index, h3_resolution, center_lat, center_lng, composite_score, score_breakdown, computed_at)
                        VALUES
                            (:h3_index, :resolution, :center_lat, :center_lng, :composite_score, :score_breakdown, datetime('now'))
                        """
                    ),
                    {
                        "h3_index": score["h3_index"],
                        "resolution": resolution,
                        "center_lat": score["center_lat"],
                        "center_lng": score["center_lng"],
                        "composite_score": score["composite_score"],
                        "score_breakdown": json.dumps(score["score_breakdown"]),
                    },
                )

        return scores

    async def run_dbscan_and_gistar(self, resolution: int = 8) -> Dict[str, int]:
        """Compute DBSCAN cluster labels and Getis-Ord Gi* values and persist."""
        async with engine.begin() as conn:
            rows = (
                await conn.execute(
                    text(
                        """
                        SELECT h3_index, center_lat, center_lng, composite_score
                        FROM h3_hex_scores
                        WHERE h3_resolution = :resolution
                        """
                    ),
                    {"resolution": resolution},
                )
            ).fetchall()

        if not rows:
            return {"total": 0, "hotspots": 0, "coldspots": 0}

        records = [
            {
                "h3_index": r[0],
                "center_lat": float(r[1]),
                "center_lng": float(r[2]),
                "composite_score": float(r[3]),
            }
            for r in rows
        ]

        # DBSCAN on high-scoring hexes
        high = [r for r in records if r["composite_score"] > 70]
        labels_map: Dict[str, int] = {r["h3_index"]: -1 for r in records}
        if len(high) >= 3:
            coords = np.array([[r["center_lat"], r["center_lng"]] for r in high])
            labels = DBSCAN(eps=0.01, min_samples=3).fit_predict(coords)
            for rec, label in zip(high, labels):
                labels_map[rec["h3_index"]] = int(label)

        # Gi*
        values = np.array([r["composite_score"] for r in records])
        mean = float(np.mean(values))
        std = float(np.std(values)) or 1.0
        gi_map: Dict[str, float] = {}
        for rec in records:
            neighbors = h3.k_ring(rec["h3_index"], 2)
            local = [next((x["composite_score"] for x in records if x["h3_index"] == n), None) for n in neighbors]
            local_vals = [v for v in local if v is not None]
            if len(local_vals) < 2:
                gi = 0.0
            else:
                expected = len(local_vals) * mean
                gi = (sum(local_vals) - expected) / (std * math.sqrt(len(local_vals)))
            gi_map[rec["h3_index"]] = float(gi)

        hotspots = 0
        coldspots = 0
        async with engine.begin() as conn:
            for rec in records:
                gi = gi_map[rec["h3_index"]]
                is_hotspot = gi > 1.96
                is_coldspot = gi < -1.96
                hotspots += int(is_hotspot)
                coldspots += int(is_coldspot)
                await conn.execute(
                    text(
                        """
                        UPDATE h3_hex_scores
                        SET cluster_label = :cluster_label,
                            gi_star_value = :gi,
                            is_hotspot = :is_hotspot,
                            is_coldspot = :is_coldspot
                        WHERE h3_index = :h3_index
                        """
                    ),
                    {
                        "cluster_label": labels_map[rec["h3_index"]],
                        "gi": gi,
                        "is_hotspot": is_hotspot,
                        "is_coldspot": is_coldspot,
                        "h3_index": rec["h3_index"],
                    },
                )

        return {"total": len(records), "hotspots": hotspots, "coldspots": coldspots}

    async def get_hex_grid_geojson(
        self,
        resolution: int = 8,
        weights: Optional[Dict[str, float]] = None,
        use_case: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return persisted hex grid as GeoJSON."""
        async with engine.begin() as conn:
            rows = (
                await conn.execute(
                    text(
                        """
                        SELECT h3_index, composite_score, score_breakdown,
                               is_hotspot, is_coldspot, gi_star_value, cluster_label
                        FROM h3_hex_scores
                        WHERE h3_resolution = :resolution
                        """
                    ),
                    {"resolution": resolution},
                )
            ).fetchall()

        features = []
        for row in rows:
            hindex = row[0]
            try:
                boundary = h3.h3_to_geo_boundary(hindex, geo_json=True)
                coords = [[float(x), float(y)] for x, y in boundary]
            except TypeError:
                boundary = h3.h3_to_geo_boundary(hindex)
                coords = [[float(lng), float(lat)] for lat, lng in boundary]
            if coords and coords[0] != coords[-1]:
                coords.append(coords[0])

            breakdown = row[2]
            if isinstance(breakdown, str):
                try:
                    breakdown = json.loads(breakdown)
                except json.JSONDecodeError:
                    breakdown = {}

            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Polygon", "coordinates": [coords]},
                    "properties": {
                        "h3_index": hindex,
                        "composite_score": float(row[1]),
                        "score_breakdown": breakdown,
                        "is_hotspot": bool(row[3]),
                        "is_coldspot": bool(row[4]),
                        "gi_star_value": float(row[5]) if row[5] is not None else None,
                        "cluster_label": int(row[6]) if row[6] is not None else -1,
                    },
                }
            )

        return {"type": "FeatureCollection", "features": features}


clustering_service = ClusteringService()
