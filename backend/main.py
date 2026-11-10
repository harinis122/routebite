# create FastAPI(), include routers, entry point only
from fastapi import FastAPI
from backend.api.recommendations import router
from backend.schemas import *

from backend.services.restaurant_service import get_all_restaurants
from backend.services.routing_service import get_route_info, get_restaurant_search_points

app = FastAPI()
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/test-places")
async def test_places(request: RecommendationRequest):
    return await get_all_restaurants(request)

@app.post("/test-route")
async def test_route(origin: LocationCoordinates, dest: LocationCoordinates, target_mins: float, flexibility_mins: float, num_samples: int):
    try:
        route_info = await get_route_info(origin, dest)
        return get_restaurant_search_points(route_info, target_mins, flexibility_mins, num_samples)
    except ValueError:
        print('no route found!')

