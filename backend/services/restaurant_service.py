# get candidate restaurants, combine Google + OSM data, normalize/enrich restaurants
from backend.clients.google_places import search_restaurants_near

from backend.schemas import Restaurant, RecommendationRequest
from backend.schemas import DietAvailability, DietaryInfo

async def get_all_restaurants(request: RecommendationRequest) -> list[Restaurant]:
    places = await search_restaurants_near(request.origin.latitude, request.origin.longitude)
    restaurants = []
    for place in places:
        restaurant = Restaurant(
            place_id=place["id"],
            name=place["displayName"]["text"],
            latitude=place["location"]["latitude"],
            longitude=place["location"]["longitude"],
            formatted_address=place.get("formattedAddress"),
            rating=place.get("rating"),
            user_rating_count=place.get("userRatingCount"),
            cuisine_tags=place.get("types", []),
        )
        restaurants.append(restaurant)

    #restaurants = get_fake_google_restaurants()
    return restaurants


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

