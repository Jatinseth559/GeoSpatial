"""
Demographic zones data generation for Ahmedabad study area.

Generates 200 realistic demographic zones with population, income, 
age distribution, and employment data following realistic urban patterns.
"""

import random
import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
import geopandas as gpd
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker
from core.models import DemographicZone
from config import settings

logger = logging.getLogger(_