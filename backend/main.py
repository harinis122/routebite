# create FastAPI(), include routers, entry point only
from fastapi import FastAPI
from backend.api.recommendations import router

api = FastAPI()
api.include_router(router)
