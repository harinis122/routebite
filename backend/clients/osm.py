# raw OSM HTTP calls
import httpx


OVERPASS_URL = "https://overpass.private.coffee/api/interpreter"


async def get_nearby_osm_restaurants(
    latitude: float,
    longitude: float,
    radius: float = 30,
) -> list[dict]:

    query = f"""
    [out:json][timeout:10];

    nwr["amenity"="restaurant"]
        (around:{radius},{latitude},{longitude});

    out center;
    """

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            OVERPASS_URL,
            data={"data": query},
            headers={
                "User-Agent": "RouteBite/1.0"
            },
        )

        response.raise_for_status()

    elements = response.json().get("elements", [])

    restaurants = []

    for element in elements:
        tags = element.get("tags", {})

        # Nodes have direct lat/lon.
        # Ways/relations get a "center" from `out center`.
        if element["type"] == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")

        # Automatically collect ANY diet:* tags that OSM has.
        dietary = {
            key.removeprefix("diet:"): value
            for key, value in tags.items()
            if key.startswith("diet:")
        }

        restaurants.append(
            {
                "osm_type": element["type"],
                "osm_id": element["id"],
                "name": tags.get("name"),
                "latitude": lat,
                "longitude": lon,
                "dietary": dietary,
            }
        )

    return restaurants
# need: osm_id: str | None = None, dietary information

