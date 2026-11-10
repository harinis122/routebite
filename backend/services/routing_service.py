import polyline
from math import radians, sin, cos, sqrt, atan2

from backend.schemas import LocationCoordinates, RouteInfo
from backend.clients.google_routes import get_route

async def get_route_info(
    origin: LocationCoordinates,
    destination: LocationCoordinates,
) -> RouteInfo:
    '''Returns RouteInfo object from origin and destination location coordinates'''

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

def get_restaurant_search_points(
    route_info: RouteInfo,
    target_minutes: float,
    flexibility_minutes: float,
    num_samples: int = 5,
) -> list[tuple[float, float]]:
    """Returns all target restaurant search points, given RouteInfo and user preferences such as minutes to restaurant"""

    coordinates = _decode_route_coordinates(
        route_info.polyline
    )

    start_fraction, end_fraction = (
        _get_stop_window_fractions(
            route_info.duration_minutes,
            target_minutes,
            flexibility_minutes,
        )
    )

    return _sample_coordinates_in_window(
        coordinates,
        start_fraction,
        end_fraction,
        num_samples,
    )



def _decode_route_coordinates(
    encoded_polyline: str,
) -> list[tuple[float, float]]:
    """
    Convert Google's encoded polyline into:
    [(latitude, longitude), ...]
    """
    return polyline.decode(encoded_polyline)


def _get_stop_window_fractions(
    total_duration_minutes: float,
    target_minutes: float,
    flexibility_minutes: float,
) -> tuple[float, float]:
    """
    Approximate what fraction of the route corresponds to the
    user's desired stop-time window.

    Example:
        route = 80 minutes
        target = 30 minutes
        flexibility = 10 minutes

        window = 20 -> 40 minutes
        fractions = 0.25 -> 0.50
    """

    earliest_minutes = max(
        0,
        target_minutes - flexibility_minutes,
    )

    latest_minutes = min(
        total_duration_minutes,
        target_minutes + flexibility_minutes,
    )

    start_fraction = earliest_minutes / total_duration_minutes
    end_fraction = latest_minutes / total_duration_minutes

    return start_fraction, end_fraction

def _distance_between_points(
    point1: tuple[float, float],
    point2: tuple[float, float],
) -> float:
    """
    Haversine distance in meters between two lat/lon points.
    """

    lat1, lon1 = point1
    lat2, lon2 = point2

    earth_radius = 6371000

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c

def _get_cumulative_distances(
    coordinates: list[tuple[float, float]],
) -> list[float]:

    distances = [0.0]

    for i in range(1, len(coordinates)):
        segment_distance = _distance_between_points(
            coordinates[i - 1],
            coordinates[i],
        )

        distances.append(
            distances[-1] + segment_distance
        )

    return distances


def _sample_coordinates_in_window(
    coordinates: list[tuple[float, float]],
    start_fraction: float,
    end_fraction: float,
    num_samples: int = 5,
) -> list[tuple[float, float]]:
    """Sample coordinates in route based on distance, not middle x coordinates"""

    if not coordinates:
        return []

    cumulative_distances = _get_cumulative_distances(
        coordinates
    )

    total_distance = cumulative_distances[-1]

    sampled_coordinates = []

    for i in range(num_samples):

        if num_samples == 1:
            sample_progress = 0.5
        else:
            sample_progress = i / (num_samples - 1)

        route_fraction = (
            start_fraction
            + sample_progress
            * (end_fraction - start_fraction)
        )

        target_distance = (
            route_fraction * total_distance
        )

        closest_index = min(
            range(len(cumulative_distances)),
            key=lambda j: abs(
                cumulative_distances[j]
                - target_distance
            ),
        )

        sampled_coordinates.append(
            coordinates[closest_index]
        )

    return sampled_coordinates

def get_detour_minutes(rest_lat, rest_long, req_origin, req_dest):
    return 5

def get_time_to_restaurant(restaurant, origin):
    return 10