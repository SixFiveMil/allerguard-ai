import os
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
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
    description="A Private, Offline-First Allergen Guardian for Tree Nut, Peanut, Coconut, and Sesame Allergies",
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

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class AnalyzeRequest(BaseModel):
    product_name: str
    ingredients_text: str
    category: Optional[str] = "general"
    dedicated_facility: Optional[bool] = False
    certified_allergen_free: Optional[bool] = False

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
        "protected_user": settings.profile.name,
        "gemma_model": settings.gemma_model,
        "tabpfn_ready": True
    }

@app.get("/api/profile")
async def get_profile():
    return settings.profile.model_dump()

@app.get("/api/demo-samples")
async def get_demo_samples():
    return [
        {
            "id": "sample-1",
            "name": "Artisanal Za'atar & Herb Flatbread",
            "category": "bakery",
            "ingredients": "Enriched unbleached wheat flour, olive oil, wild thyme, sumac, toasted sesame seeds, sesame oil, sea salt.",
            "dedicated_facility": False,
            "certified_allergen_free": False,
            "expected_verdict": "DANGER",
            "rationale": "Direct toasted sesame seeds and sesame oil: severe anaphylaxis hazard."
        },
        {
            "id": "sample-2",
            "name": "Dairy-Free Artisanal Vegan Mozzarella",
            "category": "dairy_alt",
            "ingredients": "Filtered water, modified potato starch, refined coconut oil, coconut cream, sea salt, natural flavors.",
            "dedicated_facility": False,
            "certified_allergen_free": False,
            "expected_verdict": "DANGER",
            "rationale": "Heavily disguised coconut oil and coconut cream in plant-based formulation: strict allergen violation."
        },
        {
            "id": "sample-3",
            "name": "Spicy Thai Satay Simmer Sauce",
            "category": "sauces",
            "ingredients": "Water, sugar, roasted peanut butter, tamari soy sauce, red chili, garlic, crushed peanuts, tahini (sesame paste).",
            "dedicated_facility": False,
            "certified_allergen_free": False,
            "expected_verdict": "DANGER",
            "rationale": "Direct dual peanut and sesame allergen triggers: critical anaphylactic emergency hazard."
        },
        {
            "id": "sample-4",
            "name": "Gourmet Creamy Caesar Dressing",
            "category": "condiments",
            "ingredients": "Canola oil, water, egg yolk, parmesan cheese, vinegar, natural flavors, spices, cold-pressed vegetable oil blend, anchovy paste.",
            "dedicated_facility": False,
            "certified_allergen_free": False,
            "expected_verdict": "CAUTION",
            "rationale": "Ambiguous 'spices', 'natural flavors', and unverified 'vegetable oil blend' frequently conceal sesame or coconut derivatives."
        },
        {
            "id": "sample-5",
            "name": "Organic Seed-Craft Rosemary Crackers",
            "category": "snacks",
            "ingredients": "Sunflower seeds, pumpkin seeds, ground chia seeds, cassava flour, cold-pressed olive oil, sea salt, organic rosemary. Certified Nut-Free. Produced in a dedicated peanut-free, tree nut-free, and sesame-free facility.",
            "dedicated_facility": True,
            "certified_allergen_free": True,
            "expected_verdict": "SAFE",
            "rationale": "Dedicated peanut/nut/sesame-free facility; sunflower & pumpkin seeds; zero coconut or sesame presence."
        }
    ]

@app.post("/api/analyze")
async def analyze_ingredients(req: AnalyzeRequest):
    result = await allerguard_agent.analyze_product(
        product_name=req.product_name,
        ingredients_text=req.ingredients_text,
        category=req.category or "general",
        dedicated_facility=bool(req.dedicated_facility),
        certified_allergen_free=bool(req.certified_allergen_free)
    )
    return JSONResponse(content=result)
