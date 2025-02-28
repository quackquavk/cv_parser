from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes import document_route

app = FastAPI(title="CV Parser API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create documents directory if it doesn't exist
os.makedirs("documents", exist_ok=True)

# Mount static files
app.mount("/documents", StaticFiles(directory="documents"), name="documents")

# Include routes
app.include_router(document_route.router, prefix="/document", tags=["Documents"])

@app.get("/")
async def root():
    return {"message": "CV Parser API is running"}
