# defines POST /recommendations, accepts request, calls service, returns response
from fastapi import APIRouter

from backend.schemas import RecommendationRequest
from backend.services.recommendation_service import get_top_five_restaurants

router = APIRouter()


@router.post("/recommendations")
def recommend(request: RecommendationRequest):
    return get_top_five_restaurants(request)


