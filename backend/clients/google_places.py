# raw Google Places HTTP calls
import httpx

from backend.config import GOOGLE_MAPS_API_KEY


PLACES_URL = "https://places.googleapis.com/v1/places:searchNearby"


async def search_restaurants_near(
    latitude: float,
    longitude: float,
    radius: float = 5000,
):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.rating,"
            "places.userRatingCount,"
            "places.types"
        ),
    }

    body = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": radius,
            }
        },
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            PLACES_URL,
            headers=headers,
            json=body,
        )

        response.raise_for_status()

        return response.json().get("places", [])
