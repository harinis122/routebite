import os
import httpx

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

async def get_route(origin: str, destination: str) -> dict:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "routes.duration,"
            "routes.distanceMeters,"
            "routes.polyline.encodedPolyline"
        ),
    }

    body = {
        "origin": {
            "address": origin
        },
        "destination": {
            "address": destination
        },
        "travelMode": "DRIVE",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            ROUTES_URL,
            headers=headers,
            json=body,
        )

        response.raise_for_status()

        return response.json()