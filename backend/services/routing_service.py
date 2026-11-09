from backend.schemas import LocationCoordinates, RouteInfo
from backend.clients.google_routes import get_route

async def get_route_info(
    origin: LocationCoordinates,
    destination: LocationCoordinates,
) -> RouteInfo:

    data = await get_route(origin.latitude, origin.longitude, destination.latitude, destination.longitude)

    routes = data.get("routes", [])

    if not routes:
        raise ValueError("No route found between origin and destination")

    route = routes[0]

    duration_seconds = float(
        route["duration"].removesuffix("s")
    )

    return RouteInfo(
        duration_minutes=duration_seconds / 60,
        distance_miles=route["distanceMeters"] / 1609.344,
        polyline=route["polyline"]["encodedPolyline"],
    )



# Route provider placeholder
def get_detour_minutes(restaurant_lat: float, restaurant_long: float, origin: str, destination: str) -> float:
    # Eventually Routes API / routing provider
    return 5

def get_time_to_restaurant(restaurant, origin):
    return 5
