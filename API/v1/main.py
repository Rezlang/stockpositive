from routes import news_routes
from routes import userRoutes
from fastapi import FastAPI

app = FastAPI()

app.include_router(news_routes.router, prefix="/news", tags=["news"])
app.include_router(userRoutes.router, prefix="/users", tags=["users"])
