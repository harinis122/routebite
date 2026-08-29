from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

api = FastAPI()

class RecommendationRequest(BaseModel):
    origin: str
    destination: str
    max_detour_minutes: int = Field(gt=0, le=60)
    cuisines: list[str]
    min_rating: float
    rating_weight: float = Field(ge=0, le=1)
    convenience_weight: float = Field(ge=0, le=1)
    cuisine_weight: float = Field(ge=0, le=0)


class Restaurant(BaseModel):
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: float
    rating_count: int
    cuisines: list[str]
    dietary_options: list[str]
    price_level: int | None


class RestaurantCandidate(BaseModel):
    restaurant: Restaurant
    detour_minutes: float
    cuisine_match: float
    convenience_match: float
    rating_match: float
    score: float




@api.post("/recommendations")
def recommend(request: RecommendationRequest):
    return request.origin, request.max_detour_minutes


def get_top_five_restaurants(request: RecommendationRequest):
    all_restaurants = []
    score_dict = {}
    
    pass



def score_restaraunt(restaurant: Restaurant) -> RestaurantCandidate:
    pass





