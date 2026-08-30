from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel, Field


api = FastAPI()


# ---------------------------------------------------------
# Request
# ---------------------------------------------------------

class RecommendationRequest(BaseModel):
    origin: str
    destination: str
    max_detour_minutes: int = Field(gt=0, le=60)
    cuisines: list[str] = Field(default_factory=[])
    dietary_restrictions: list[DietaryRestriction] = Field(default_factory=[])
    min_rating: float | None = Field(default=None, ge=0, le=5)
    rating_weight: float = Field(default=0.5, ge=0, le=1)
    preference_weight: float = Field(default=0.5, ge=0, le=1)

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


# ---------------------------------------------------------
# API
# ---------------------------------------------------------

@api.post("/recommendations")
def recommend(request: RecommendationRequest) -> list[RestaurantCandidate]:
    return get_top_five_restaurants(request)


# ---------------------------------------------------------
# Ranking
# ---------------------------------------------------------

def get_top_five_restaurants(request: RecommendationRequest) -> list[RestaurantCandidate]:
    all_restaurants = get_all_restaurants(request)
    candidates = []
    for restaurant in all_restaurants:
        candidate = score_restaurant(restaurant, request)
        if candidate is not None:
            candidates.append(candidate)
    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates[:5]


def score_restaurant(restaurant: Restaurant, request: RecommendationRequest) -> RestaurantCandidate | None:
    """Scores restaurant, returns None if restaurant does not meet minimum requirements"""
    # Hard dietary filter
    if not satisfies_dietary_requirements(restaurant, request.dietary_restrictions):
        return None

    # Minimum rating filter
    if request.min_rating is not None:
        if restaurant.rating is None or restaurant.rating < request.min_rating:
            return None

    # Detour filter
    detour_minutes = get_detour_minutes(restaurant.latitude, restaurant.longitude, request.origin, request.destination)
    if detour_minutes > request.max_detour_minutes:
        return None

    # Soft scores
    cuisine_match = get_cuisine_score(restaurant, request)
    rating_match = get_rating_score(restaurant)
    convenience_match = get_convenience_score(detour_minutes, request.max_detour_minutes)
    soft_weight_total = request.preference_weight + request.rating_weight

    if soft_weight_total == 0:
        preference_weight = 0.5
        rating_weight = 0.5
    else:
        preference_weight = request.preference_weight / soft_weight_total
        rating_weight = request.rating_weight / soft_weight_total

    score = (0.30 * convenience_match + 0.70 * (preference_weight * cuisine_match + rating_weight * rating_match))

    return RestaurantCandidate(
        restaurant=restaurant,
        detour_minutes=detour_minutes,
        cuisine_match=cuisine_match,
        convenience_match=convenience_match,
        rating_match=rating_match,
        score=round(score, 3),
    )


def satisfies_dietary_requirements(restaurant: Restaurant, restrictions: list[DietaryRestriction]) -> bool:
    """Filters restaurant by dietary requirements"""
    for restriction in restrictions:
        if restriction == DietaryRestriction.VEGETARIAN:
            if restaurant.dietary.vegetarian not in {DietAvailability.YES, DietAvailability.ONLY}:
                return False

        elif restriction == DietaryRestriction.PURE_VEGETARIAN:
            if (restaurant.dietary.vegetarian != DietAvailability.ONLY):
                return False

        elif restriction == DietaryRestriction.VEGAN:
            if restaurant.dietary.vegan not in {DietAvailability.YES, DietAvailability.ONLY}:
                return False

        elif restriction == DietaryRestriction.PURE_VEGAN:
            if (restaurant.dietary.vegan != DietAvailability.ONLY):
                return False

        elif restriction == DietaryRestriction.HALAL:
            if restaurant.dietary.halal not in {DietAvailability.YES, DietAvailability.ONLY}:
                return False

        elif restriction == DietaryRestriction.KOSHER:
            if restaurant.dietary.kosher not in {DietAvailability.YES, DietAvailability.ONLY}:
                return False

        elif restriction == DietaryRestriction.GLUTEN_FREE:
            if restaurant.dietary.gluten_free not in {DietAvailability.LIMITED, DietAvailability.YES, DietAvailability.ONLY}:
                return False

    return True


# ---------------------------------------------------------
# Soft score components
# ---------------------------------------------------------

def get_cuisine_score(restaurant: Restaurant, request: RecommendationRequest) -> float:
    if not request.cuisines:
        return 1.0
    user_cuisines = {cuisine.lower() for cuisine in request.cuisines}
    restaurant_cuisines = {cuisine.lower() for cuisine in restaurant.cuisines}
    if user_cuisines & restaurant_cuisines:
        return 1.0
    return 0.0

def get_rating_score(restaurant: Restaurant) -> float:
    if restaurant.rating is None:
        return 0.0
    return restaurant.rating / 5.0

def get_convenience_score(detour_minutes: float, max_detour_minutes: float) -> float:
    # 0-minute detour -> 1.0, max allowed detour -> 0.0
    return max(0.0, 1 - detour_minutes / max_detour_minutes)


# ---------------------------------------------------------
# Provider layer
# ---------------------------------------------------------

def get_all_restaurants(request: RecommendationRequest) -> list[Restaurant]:

    # Eventually:
    #
    # 1. Google Places -> candidate restaurants
    # 2. OSM -> dietary information
    # 3. Merge both into Restaurant objects
    #
    # For now return fake data.

    restaurants = get_fake_google_restaurants()
    return [enrich_with_fake_osm_data(restaurant) for restaurant in restaurants]


def get_fake_google_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            google_place_id="google_1",
            name="Madras Cafe",
            address="123 Main St",
            latitude=37.70,
            longitude=-121.93,
            rating=4.6,
            rating_count=843,
            price_level=2,
            cuisines=[
                "indian",
                "south_indian",
            ],
            google_serves_vegetarian=True,
        ),

        Restaurant(
            google_place_id="google_2",
            name="Vegan Bowl",
            address="456 Main St",
            latitude=37.71,
            longitude=-121.94,
            rating=4.8,
            rating_count=320,
            price_level=2,
            cuisines=[
                "vegan",
                "asian",
            ],
            google_serves_vegetarian=True,
        ),
    ]


def enrich_with_fake_osm_data(
    restaurant: Restaurant,
) -> Restaurant:

    # Pretend this information came from:
    #
    # diet:vegetarian
    # diet:vegan
    # diet:halal
    # diet:kosher
    # diet:gluten_free

    if restaurant.name == "Madras Cafe":

        restaurant.osm_id = "osm_123"

        restaurant.dietary = DietaryInfo(
            vegetarian=DietAvailability.ONLY,
            vegan=DietAvailability.YES,
            halal=DietAvailability.UNKNOWN,
            kosher=DietAvailability.UNKNOWN,
            gluten_free=DietAvailability.LIMITED,
        )

    elif restaurant.name == "Vegan Bowl":

        restaurant.osm_id = "osm_456"

        restaurant.dietary = DietaryInfo(
            vegetarian=DietAvailability.ONLY,
            vegan=DietAvailability.ONLY,
            halal=DietAvailability.UNKNOWN,
            kosher=DietAvailability.UNKNOWN,
            gluten_free=DietAvailability.YES,
        )

    return restaurant


# Route provider placeholder
def get_detour_minutes(restaurant_lat: float, restaurant_long: float, origin: str, destination: str) -> float:
    # Eventually Routes API / routing provider
    return 5
