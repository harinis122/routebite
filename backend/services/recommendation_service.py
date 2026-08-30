# cuisine/rating/convenience scoring, dietary filtering

from backend.schemas import RecommendationRequest, RestaurantCandidate, Restaurant
from backend.schemas import DietaryRestriction, DietAvailability
from backend.services.restaurant_service import get_all_restaurants
from backend.services.routing_service import get_detour_minutes, get_time_to_restaurant

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
    # Minimum rating filter
    if request.min_rating is not None:
        if restaurant.rating is None or restaurant.rating < request.min_rating:
            return None

    # Hard dietary filter
    if not satisfies_dietary_requirements(restaurant, request.dietary_restrictions):
        return None

    # Hard time filter
    time_to_restaurant = get_time_to_restaurant(restaurant, request.origin)
    if request.desired_stop_window:
        if not request.desired_stop_window.earliest_minutes <= time_to_restaurant <= request.desired_stop_window.latest_minutes:
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

