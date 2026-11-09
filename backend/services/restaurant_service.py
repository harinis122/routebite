# get candidate restaurants, combine Google + OSM data, normalize/enrich restaurants
import httpx
import math # OSM matching
from difflib import SequenceMatcher # OSM matching

from backend.clients.google_places import get_nearby_restaurants

from backend.schemas import Restaurant, RecommendationRequest


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
        restaurants.append(restaurant)

    return restaurants
