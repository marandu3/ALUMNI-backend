from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import router as user_router
from routes.news import router as news_router
import uvicorn

app = FastAPI()

# ✅ Allow requests from any origin (cross-platform: web, mobile, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Accept requests from any domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (e.g., Authorization, Content-Type)
)

# ✅ Include your route groups
app.include_router(user_router, tags=["user"])
app.include_router(news_router, tags=["news"])

# ✅ Test endpoint
@app.get("/")
async def main():
    return {"message": "Hello World"}

# ✅ Run the application using: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)