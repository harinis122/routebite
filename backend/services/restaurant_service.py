# get candidate restaurants, combine Google + OSM data, normalize/enrich restaurants
import math # OSM matching
from difflib import SequenceMatcher # OSM matching

from backend.clients.google_places import get_nearby_restaurants
from backend.clients.osm import get_nearby_osm_restaurants

from backend.schemas import Restaurant, RecommendationRequest
from backend.schemas import DietaryInfo, DietAvailability


# retrieve restaurants from google places, enriched with OSM
async def get_all_restaurants(request: RecommendationRequest) -> list[Restaurant]:
    places = await get_nearby_restaurants(request.origin.latitude, request.origin.longitude)
    restaurants = []
    for place in places:
        restaurant = Restaurant(
            google_place_id=place["id"],
            name=place["displayName"]["text"],
            address=place.get("formattedAddress"),
            latitude=place["location"]["latitude"],
            longitude=place["location"]["longitude"],
            rating=place.get("rating"),
            rating_count=place.get("userRatingCount"),
            price_level=place.get("priceLevel"),
            cuisines=place.get("types", []),
        )
        restaurant = await enrich_with_osm_data(restaurant)
        restaurants.append(restaurant)

    return restaurants

async def enrich_with_osm_data(restaurant: Restaurant) -> Restaurant:
    osm_candidates = await get_nearby_osm_restaurants(
    restaurant.latitude,
    restaurant.longitude,
    )

    osm_match = find_best_osm_match(
        restaurant.name,
        restaurant.latitude,
        restaurant.longitude,
        osm_candidates,
    )

    if osm_match:
        restaurant.osm_id = osm_match["osm_id"]
        restaurant.dietary_info = build_dietary_info(
            osm_match.get("dietary", {})
        )
    
    return restaurant


# OSM matching
def normalize_name(name: str) -> str:
    return "".join(
        char.lower()
        for char in name
        if char.isalnum()
    )

def name_similarity(name1: str, name2: str) -> float:
    return SequenceMatcher(
        None,
        normalize_name(name1),
        normalize_name(name2),
    ).ratio()

def distance_meters(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:

    earth_radius = 6_371_000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return earth_radius * c

def find_best_osm_match(
    google_name: str,
    google_latitude: float,
    google_longitude: float,
    osm_candidates: list[dict],
) -> dict | None:

    possible_matches = []

    for candidate in osm_candidates:

        if candidate["name"] is None:
            continue

        if (
            candidate["latitude"] is None
            or candidate["longitude"] is None
        ):
            continue

        similarity = name_similarity(
            google_name,
            candidate["name"],
        )

        distance = distance_meters(
            google_latitude,
            google_longitude,
            candidate["latitude"],
            candidate["longitude"],
        )

        # Avoid matching a nearby unrelated restaurant.
        if similarity >= 0.65:
            possible_matches.append(
                (
                    similarity,
                    distance,
                    candidate,
                )
            )

    if not possible_matches:
        return None

    # Name match is prioritized; if names are equally similar, choose closest restaurant.
    possible_matches.sort(
        key=lambda item: (-item[0], item[1])
    )

    return possible_matches[0][2]

def build_dietary_info(raw_dietary: dict[str, str]) -> DietaryInfo:
    """
    Convert raw OSM diet:* values into RouteBite's DietaryInfo model.

    - Ignores dietary categories RouteBite doesn't support.
    - Converts invalid OSM values to UNKNOWN.
    - Missing dietary information defaults to UNKNOWN.
    """

    supported_fields = {
        "vegetarian",
        "vegan",
        "halal",
        "kosher",
        "gluten_free",
    }

    cleaned_dietary = {}

    for diet, value in raw_dietary.items():

        # Ignore OSM dietary tags RouteBite does not support
        if diet not in supported_fields:
            continue

        normalized_value = value.strip().lower()

        try:
            cleaned_dietary[diet] = DietAvailability(normalized_value)
        except ValueError:
            cleaned_dietary[diet] = DietAvailability.UNKNOWN

    return DietaryInfo(**cleaned_dietary)

