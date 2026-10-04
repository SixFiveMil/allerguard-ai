import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class FriendProfile(BaseModel):
    name: str = "Maya"
    primary_conditions: list[str] = [
        "Celiac Disease (Strict Gluten-Free: 0 ppm wheat, barley, rye, spelt, malt, brewer's yeast)",
        "Severe Tree Nut Allergy (Almond, Walnut, Cashew, Pecan, Pistachio, Hazelnut)"
    ]
    cross_contamination_tolerance: str = "Zero tolerance (shared equipment, shared oil fryers, and bulk bins prohibited)"
    high_risk_hidden_ingredients: list[str] = [
        "natural flavors", "malt extract", "modified food starch", "caramel color",
        "hydrolyzed vegetable protein", "smoke flavoring", "dextrin", "spices (unspecified)",
        "emulsifiers", "praline", "marzipan", "gianduja", "nougat"
    ]
    emergency_protocol: str = "Epinephrine autoinjector required immediately on accidental ingestion; seek emergency medical care."

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
    elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Rachel (clear, calm voice)

    # Sentry Agent Tracing
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    sentry_environment: str = os.getenv("SENTRY_ENVIRONMENT", "production")

    # Default Friend Profile
    friend: FriendProfile = FriendProfile()

settings = Settings()
