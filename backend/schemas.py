from enum import Enum
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Request
# ---------------------------------------------------------

class RecommendationRequest(BaseModel):
    origin: str
    destination: str
    desired_stop_window: StopWindow | None
    max_detour_minutes: int = Field(gt=0, le=60)
    cuisines: list[str] = Field(default_factory=[])
    dietary_restrictions: list[DietaryRestriction] = Field(default_factory=[])
    min_rating: float | None = Field(default=None, ge=0, le=5)
    rating_weight: float = Field(default=0.5, ge=0, le=1)
    preference_weight: float = Field(default=0.5, ge=0, le=1)

# ---------------------------------------------------------
# Dietary Info
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
    price_level: int | None = None

    cuisines: list[str] = Field(default_factory=list)

    # Google has servesVegetarianFood, we keep this separately before merging it with OSM
    google_serves_vegetarian: bool | None = None

    # Primarily OSM dietary enrichment
    dietary: DietaryInfo = Field(default_factory=DietaryInfo)


class RestaurantCandidate(BaseModel):
    restaurant: Restaurant
    detour_minutes: float
    cuisine_match: float
    convenience_match: float
    rating_match: float
    score: float
