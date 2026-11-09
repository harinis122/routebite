# create FastAPI(), include routers, entry point only
from fastapi import FastAPI
from backend.api.recommendations import router
from backend.schemas import *

from backend.services.restaurant_service import get_all_restaurants
from backend.services.routing_service import get_route_info

app = FastAPI()
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/test-places")
async def test_places(request: RecommendationRequest):
    return await get_all_restaurants(request)

@app.post("/test-route")
async def test_route(origin: LocationCoordinates, dest: LocationCoordinates):
    try:
        return await get_route_info(origin, dest)
    except ValueError:
        print('no route found!')

