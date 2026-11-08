# create FastAPI(), include routers, entry point only
from fastapi import FastAPI
from fastapi import Query
from backend.api.recommendations import router

from backend.clients.google_places import search_restaurants_near

app = FastAPI()
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test-places")
async def test_places(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
):
    return await search_restaurants_near(latitude, longitude)