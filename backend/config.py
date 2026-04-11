from functools import lru_cache
from typing import List, Tuple

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./geositedb.sqlite"
    )
    REDIS_URL: str = Field(default="memory://localhost")
    STUDY_AREA_BBOX: str = Field(default="72.45,22.87,72.75,23.15")
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:8080")
    CACHE_TTL_SECONDS: int = Field(default=300)
    APP_NAME: str = Field(default="GeoSpatial Site Readiness Analyzer")

    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        """Study area bounding box as (min_lng, min_lat, max_lng, max_lat)."""
        parts = [p.strip() for p in self.STUDY_AREA_BBOX.split(",")]
        if len(parts) != 4:
            raise ValueError("STUDY_AREA_BBOX must contain 4 comma-separated values")
        min_lng, min_lat, max_lng, max_lat = (float(v) for v in parts)
        return min_lng, min_lat, max_lng, max_lat

    @property
    def cors_origins_list(self) -> List[str]:
        """Allowed CORS origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
