from enum import Enum
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Request
# ---------------------------------------------------------

class RecommendationRequest(BaseModel):
    origin: LocationCoordinates
    destination: LocationCoordinates
    desired_stop_window: StopWindow | None
    max_detour_minutes: int = Field(gt=0, le=60)
    cuisines: list[str] = Field(default_factory=[])
    dietary_restrictions: list[DietaryRestriction] = Field(default_factory=[])
    min_rating: float | None = Field(default=None, ge=0, le=5)
    rating_weight: float = Field(default=0.5, ge=0, le=1)
    preference_weight: float = Field(default=0.5, ge=0, le=1)

class LocationCoordinates(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

# ---------------------------------------------------------
# Other Preferences
# ---------------------------------------------------------
class StopWindow(BaseModel):
    earliest_minutes: int
    latest_minutes: int


# ---------------------------------------------------------
# Dietary Info
# ---------------------------------------------------------

class DietaryRestriction(str, Enum):
    VEGETARIAN = "vegetarian"
    PURE_VEGETARIAN = "pure_vegetarian"
    VEGAN = "vegan"
    PURE_VEGAN = "pure_vegan"
    HALAL = "halal"
    KOSHER = "kosher"
    GLUTEN_FREE = "gluten_free"

class DietAvailability(str, Enum):
    ONLY = "only"
    YES = "yes"
    LIMITED = "limited"
    NO = "no"
    UNKNOWN = "unknown"

class DietaryInfo(BaseModel):
    vegetarian: DietAvailability = DietAvailability.UNKNOWN
    vegan: DietAvailability = DietAvailability.UNKNOWN
    halal: DietAvailability = DietAvailability.UNKNOWN
    kosher: DietAvailability = DietAvailability.UNKNOWN
    gluten_free: DietAvailability = DietAvailability.UNKNOWN


# ---------------------------------------------------------
# Restaurant
# ---------------------------------------------------------
# coming later once integration with osm is complete!

class Restaurant(BaseModel):
    # Provider IDs
    google_place_id: str | None = None
    osm_id: str | None = None

    name: str
    address: str

    latitude: float
    longitude: float

    # Google Places
    rating: float | None = None
    rating_count: int = 0
    price_level: str | None = None

    cuisines: list[str] = Field(default_factory=list)

    # OSM dietary enrichment
    dietary_info: DietaryInfo = Field(default_factory=DietaryInfo)

'''
class Restaurant(BaseModel):
    place_id: str
    name: str
    latitude: float
    longitude: float
    formatted_address: str
    rating: float | None = None
    user_rating_count: int | None = None
    cuisine_tags: list[str] = Field(default_factory=list)
'''

class RestaurantCandidate(BaseModel):
    restaurant: Restaurant
    detour_minutes: float
    cuisine_match: float
    convenience_match: float
    rating_match: float
    score: float


# ---------------------------------------------------------
# Routing
# ---------------------------------------------------------

class RouteInfo(BaseModel):
    duration_minutes: float
    distance_miles: float
    polyline: str


'''
# ---------------------------------------------------------
# Price Level Normalization
# ---------------------------------------------------------
PRICE_LEVEL_MAP = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}
price_level = PRICE_LEVEL_MAP.get(place.get("priceLevel"))
'''