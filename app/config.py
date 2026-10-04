import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class UserAllergyProfile(BaseModel):
    name: str = "Joshua"
    primary_conditions: list[str] = [
        "Severe Tree Nut Allergy (Almonds, Walnuts, Cashews, Pecans, Pistachios, Hazelnuts, Macadamia)",
        "Severe Peanut Allergy (Arachis hypogaea / Legume allergen with high anaphylaxis risk)",
        "Coconut Allergy (Drupe allergen heavily hidden in dairy-free & plant-based formulations)",
        "Sesame Allergy (FDA Major Allergen: hidden in spices, tahini, oils, and bakery glazes)"
    ]
    cross_contamination_tolerance: str = "Strict Zero Tolerance (shared manufacturing equipment, shared fryers, and uncertified bulk handling prohibited)"
    high_risk_hidden_ingredients: list[str] = [
        # Sesame hidden terms
        "tahini", "sesame", "sesamum indicum", "halvah", "benne", "gomasio", "sesame flour", "til", "gingelly",
        # Coconut hidden terms
        "coconut", "coconut milk", "coconut oil", "coconut aminos", "cream of coconut", "mct oil", "copra",
        # Peanut hidden terms
        "peanut", "groundnut", "beer nuts", "arachis oil", "peanut flour", "hydrolyzed peanut protein",
        # Tree nut hidden terms
        "almond", "walnut", "cashew", "pecan", "pistachio", "hazelnut", "brazil nut", "macadamia",
        "marzipan", "praline", "gianduja", "nougat", "nut meal", "nut paste",
        # Ambiguous camouflage terms
        "natural flavors", "natural flavoring", "artificial flavors", "spices", "vegetable oil blend",
        "hydrolyzed plant protein", "emulsifiers", "cold-pressed oil"
    ]
    emergency_protocol: str = "Immediate Epinephrine Auto-Injector (EpiPen / Auvi-Q) upon suspected exposure; call 911."

class Settings(BaseModel):
    # App
    app_name: str = "AllerGuard AI"
    environment: str = os.getenv("ENVIRONMENT", "development")
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")

    # Gemma (Open-Weight Model)
    gemma_api_base: str = os.getenv("GEMMA_API_BASE", "http://localhost:11434/v1")
    gemma_model: str = os.getenv("GEMMA_MODEL", "google/gemma-2-9b-it")
    gemma_api_key: str = os.getenv("GEMMA_API_KEY", "ollama")

    # TabPFN Foundation Model
    tabpfn_enabled: bool = os.getenv("TABPFN_ENABLED", "true").lower() in ("true", "1", "yes")

    # SerpApi Web Grounding
    serpapi_api_key: str = os.getenv("SERPAPI_API_KEY", "")

    # ElevenLabs Audio Accessibility
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    # Sentry Agent Tracing
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    sentry_environment: str = os.getenv("SENTRY_ENVIRONMENT", "production")

    # User Profile
    profile: UserAllergyProfile = UserAllergyProfile()

settings = Settings()
