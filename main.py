from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import router as user_router
from routes.news import router as news_router
import os
port = int(os.environ.get("PORT", 8000))

#using the port for deployment
import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0", port=port, reload=True)   


app = FastAPI()

# Improved CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular dev server
        "https://your-frontend-domain.com"  # Your production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Explicit OPTIONS handler for /api/user
@app.options("/api/user")
async def user_options():
    return {"message": "OK"}

# Include routers
app.include_router(user_router, prefix="/api", tags=["user"])
app.include_router(news_router, prefix="/api", tags=["news"])

# Root endpoint
@app.get("/")
async def root():
    return {"status": "Alumni API is running"}

# Production configuration
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=2 if os.environ.get("ENV") == "production" else 1,
        reload=os.environ.get("ENV") != "production"
    )