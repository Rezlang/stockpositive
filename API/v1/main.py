from routes import news_routes
from fastapi import FastAPI

app = FastAPI()

app.include_router(news_routes.router, prefix="/news")
