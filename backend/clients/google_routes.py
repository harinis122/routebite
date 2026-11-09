import httpx
from backend.config import GOOGLE_MAPS_API_KEY

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

async def get_route(origin_lat: float, origin_long: float, destination_lat: float, destination_long: float) -> dict:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "routes.duration,"
            "routes.distanceMeters,"
            "routes.polyline.encodedPolyline"
        ),
    }

    body = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin_lat,
                    "longitude": origin_long,
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination_lat,
                    "longitude": destination_long,
                }
            }
        },
        "travelMode": "DRIVE",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            ROUTES_URL,
            headers=headers,
            json=body,
        )

        response.raise_for_status()

        return response.json()

