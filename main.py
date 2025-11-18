import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document
from schemas import Lead

app = FastAPI(title="Flooring Pro API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "name": "Flooring Pro API",
        "message": "Backend running",
        "endpoints": ["/api/hello", "/api/services", "/api/lead", "/test"],
    }

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# Public services list for the website
class Service(BaseModel):
    id: str
    title: str
    description: str
    features: List[str]
    image: Optional[str] = None

SERVICES: List[Service] = [
    Service(
        id="carpet",
        title="Carpet Installation",
        description="Soft, warm, and durable carpets for homes and offices.",
        features=[
            "Wall-to-wall installation",
            "High-traffic and stain-resistant options",
            "Removal and disposal of old carpet",
            "Underlay and edging included",
        ],
        image="/images/carpet.jpg",
    ),
    Service(
        id="wood",
        title="Hardwood Flooring",
        description="Premium hardwood floors: timeless look with professional installation.",
        features=[
            "Solid and engineered hardwood",
            "Sanding, staining, and refinishing",
            "Custom patterns (herringbone, chevron)",
            "Moisture barrier and leveling",
        ],
        image="/images/wood.jpg",
    ),
    Service(
        id="laminate",
        title="Laminate & Vinyl",
        description="Affordable, durable, and water-resistant laminate and LVT/LVP options.",
        features=[
            "Click-lock floating floors",
            "Waterproof vinyl planks",
            "Underlayment and trim work",
            "Quick turnarounds",
        ],
        image="/images/laminate.jpg",
    ),
    Service(
        id="tile",
        title="Tile & Stone",
        description="Porcelain, ceramic, and natural stone for kitchens, baths, and more.",
        features=[
            "Backer board and waterproofing",
            "Custom patterns and mosaics",
            "Grout sealing",
            "Heated floor compatible",
        ],
        image="/images/tile.jpg",
    ),
]

@app.get("/api/services", response_model=List[Service])
def get_services():
    return SERVICES

# Lead creation endpoint
@app.post("/api/lead")
def create_lead(lead: Lead):
    try:
        lead_id = create_document("lead", lead)
        return {"status": "ok", "id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
