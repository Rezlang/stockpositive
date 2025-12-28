from routes import newsRoutes
from routes import userRoutes
from routes import feedRoutes
from fastapi import FastAPI

app = FastAPI()

app.include_router(newsRoutes.router, prefix="/news", tags=["news"])
app.include_router(userRoutes.router, prefix="/users", tags=["users"])
app.include_router(feedRoutes.router, prefix="/feeds", tags=["feeds"])
