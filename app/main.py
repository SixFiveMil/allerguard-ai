import os
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.core.sentry_tracing import init_sentry
from app.core.agent import allerguard_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_sentry()
    yield

app = FastAPI(
    title=settings.app_name,
    description="A Private, Offline-First Dietary Guardian for Severe Celiac & Tree Nut Allergies",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class AnalyzeRequest(BaseModel):
    product_name: str
    ingredients_text: str
    category: Optional[str] = "general"
    dedicated_facility: Optional[bool] = False
    certified_gf: Optional[bool] = False

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>AllerGuard AI Backend Running</h1>")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "friend": settings.friend.name,
        "gemma_model": settings.gemma_model,
        "tabpfn_ready": True
    }

@app.get("/api/profile")
async def get_profile():
    return settings.friend.model_dump()

@app.get("/api/demo-samples")
async def get_demo_samples():
    return [
        {
            "id": "sample-1",
            "name": "Trader's Oven Pretzel Crisps",
            "category": "snacks",
            "ingredients": "Enriched flour (wheat flour, niacin, reduced iron, thiamin mononitrate), malt extract, salt, soybean oil, barley yeast.",
            "dedicated_facility": False,
            "certified_gf": False,
            "expected_verdict": "DANGER",
            "rationale": "Direct wheat flour and barley malt: severe activation of Celiac auto-antibodies."
        },
        {
            "id": "sample-2",
            "name": "PeakFuel Dark Chocolate Nut-Crunch Bar",
            "category": "energy_bar",
            "ingredients": "Soy protein isolate, chicory root fiber, dark chocolate coating (sugar, cocoa butter, soy lecithin), natural flavors, cashew butter, almond pieces. May contain traces of walnuts and milk.",
            "dedicated_facility": False,
            "certified_gf": False,
            "expected_verdict": "DANGER",
            "rationale": "Direct cashew & almond allergens with tree nut shared-line advisory: severe anaphylaxis risk."
        },
        {
            "id": "sample-3",
            "name": "Country Ranch Gourmet Salad Dressing",
            "category": "salad_dressing",
            "ingredients": "Canola oil, water, egg yolk, modified food starch, vinegar, natural flavors, spices, caramel color, xanthan gum, polysorbate 60.",
            "dedicated_facility": False,
            "certified_gf": False,
            "expected_verdict": "CAUTION",
            "rationale": "Contains ambiguous modified food starch and unlisted natural flavors without GF certification."
        },
        {
            "id": "sample-4",
            "name": "Siete Certified Sea Salt Cassava Chips",
            "category": "chips_corn",
            "ingredients": "Cassava flour, avocado oil, coconut flour, ground chia seed, sea salt. Certified Gluten-Free. Produced in a dedicated gluten-free and tree nut-free facility.",
            "dedicated_facility": True,
            "certified_gf": True,
            "expected_verdict": "SAFE",
            "rationale": "Certified Gluten-Free (<10ppm), single-origin grains, dedicated nut-free facility."
        }
    ]

@app.post("/api/analyze")
async def analyze_ingredients(req: AnalyzeRequest):
    result = await allerguard_agent.analyze_product(
        product_name=req.product_name,
        ingredients_text=req.ingredients_text,
        category=req.category or "general",
        dedicated_facility=bool(req.dedicated_facility),
        certified_gf=bool(req.certified_gf)
    )
    return JSONResponse(content=result)
