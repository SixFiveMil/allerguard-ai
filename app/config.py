import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

ALLERGEN_REGISTRY: dict[str, dict] = {
    "tree_nuts": {
        "label": "Tree Nuts",
        "description": "Almonds, walnuts, cashews, pecans, pistachios, hazelnuts, macadamias, brazil nuts",
        "triggers": [
            "almond", "almonds", "almond flour", "almond milk", "almond butter", "almond paste",
            "walnut", "walnuts", "cashew", "cashews", "cashew butter", "cashew milk",
            "pecan", "pecans", "pistachio", "pistachios", "hazelnut", "hazelnuts", "filbert",
            "brazil nut", "brazil nuts", "macadamia", "macadamias", "pine nut", "pine nuts",
            "marzipan", "praline", "gianduja", "nougat", "nut meal", "nut paste"
        ],
        "substitutes": "Pumpkin seeds, sunflower seed butter (SunButter), roasted watermelon seeds, oats"
    },
    "peanuts": {
        "label": "Peanuts",
        "description": "Arachis hypogaea / Legume allergen with high anaphylaxis risk",
        "triggers": [
            "peanut", "peanuts", "peanut butter", "peanut oil", "peanut flour", "arachis hypogaea",
            "arachis oil", "groundnut", "groundnuts", "beer nuts", "hydrolyzed peanut protein"
        ],
        "substitutes": "Sunflower seed butter, roasted soy nuts, roasted chickpeas"
    },
    "coconut": {
        "label": "Coconut",
        "description": "Drupe allergen heavily hidden in dairy-free & vegan alternatives",
        "triggers": [
            "coconut", "coconut oil", "coconut milk", "coconut cream", "cream of coconut",
            "coconut water", "coconut flour", "coconut aminos", "coconut sugar", "mct oil", "copra",
            "sodium cocoate"
        ],
        "substitutes": "Oat milk, flaxseed milk, soy milk, olive oil, avocado oil"
    },
    "sesame": {
        "label": "Sesame",
        "description": "FDA Major Allergen: hidden in tahini, halva, spices, and bakery glazes",
        "triggers": [
            "sesame", "sesame seed", "sesame seeds", "sesame oil", "sesame paste",
            "tahini", "tahina", "halvah", "halva", "benne", "benne seed", "gomasio",
            "sesamum indicum", "sesame flour", "til", "gingelly"
        ],
        "substitutes": "Hemp seeds, chia seeds, poppy seeds, sunflower seed paste"
    },
    "gluten_celiac": {
        "label": "Gluten / Wheat / Celiac",
        "description": "Wheat, barley, rye, malt, triticale, spelt, farro, kamut (0 ppm Celiac threshold)",
        "triggers": [
            "wheat", "barley", "rye", "malt", "malt extract", "malt flavoring", "brewer's yeast",
            "spelt", "kamut", "farro", "bulgur", "semolina", "durum", "triticale", "seitan",
            "vital wheat gluten", "wheat flour", "wheat starch", "hydrolyzed wheat protein"
        ],
        "substitutes": "Certified Gluten-Free brown rice, quinoa, millet, cassava flour, certified GF oats"
    },
    "dairy": {
        "label": "Dairy / Milk",
        "description": "Cow's milk, whey, casein, lactose, butter, ghee, cheese",
        "triggers": [
            "milk", "dairy", "whey", "casein", "caseinate", "sodium caseinate", "lactose",
            "butter", "buttermilk", "butter oil", "ghee", "cheese", "cream", "sour cream",
            "curds", "lactalbumin", "lactoglobulin", "milk solids"
        ],
        "substitutes": "Oat milk, soy yogurt, dairy-free nutritional yeast, olive oil"
    },
    "eggs": {
        "label": "Eggs",
        "description": "Albumen, egg whites, egg yolks, mayonnaise, lysozyme",
        "triggers": [
            "egg", "eggs", "egg white", "egg whites", "egg yolk", "egg yolks", "albumen",
            "albumin", "mayonnaise", "meringue", "ovalbumin", "lysozyme", "surimi", "globulin"
        ],
        "substitutes": "Aquafaba (chickpea brine), flax eggs, applesauce, commercial vegan egg replacers"
    },
    "soy": {
        "label": "Soy",
        "description": "Soybeans, edamame, soy protein, soy lecithin, miso, tofu, tempeh",
        "triggers": [
            "soy", "soya", "soybean", "soybeans", "soy protein", "soy lecithin", "soy sauce",
            "edamame", "miso", "tofu", "tempeh", "natto", "tamari", "hydrolyzed soy protein"
        ],
        "substitutes": "Coconut aminos (if not allergic to coconut), chickpea miso, nutritional yeast"
    },
    "fish": {
        "label": "Fish",
        "description": "Finned fish (salmon, tuna, cod, tilapia, anchovy, worcestershire sauce)",
        "triggers": [
            "fish", "salmon", "tuna", "cod", "halibut", "tilapia", "trout", "anchovy", "anchovies",
            "fish sauce", "worcestershire sauce", "isinglass", "caesar dressing"
        ],
        "substitutes": "Algae oil, kelp seasoning, plant-based vegan fish alternatives"
    },
    "shellfish": {
        "label": "Crustacean & Molluscan Shellfish",
        "description": "Shrimp, crab, lobster, prawns, clams, oysters, mussels, squid, calamari",
        "triggers": [
            "shrimp", "prawn", "prawns", "crab", "lobster", "crawfish", "crayfish",
            "clam", "clams", "mussel", "mussels", "oyster", "oysters", "scallop", "scallops",
            "squid", "calamari", "octopus", "krill"
        ],
        "substitutes": "Mushrooms (king oyster), hearts of palm, artichoke hearts"
    }
}

class UserAllergyProfile(BaseModel):
    name: str = "Joshua"
    selected_allergens: list[str] = ["tree_nuts", "peanuts", "coconut", "sesame"]
    custom_allergens: list[str] = []
    cross_contamination_tolerance: str = "Strict Zero Tolerance (shared equipment & facilities prohibited)"
    emergency_protocol: str = "Immediate Epinephrine Auto-Injector (EpiPen / Auvi-Q) upon suspected exposure; call 911."

    def get_all_triggers(self) -> list[str]:
        triggers = []
        for key in self.selected_allergens:
            if key in ALLERGEN_REGISTRY:
                triggers.extend(ALLERGEN_REGISTRY[key]["triggers"])
        triggers.extend([c.lower().strip() for c in self.custom_allergens if c.strip()])
        return list(set(triggers))

    def get_allergen_labels(self) -> list[str]:
        labels = []
        for key in self.selected_allergens:
            if key in ALLERGEN_REGISTRY:
                labels.append(ALLERGEN_REGISTRY[key]["label"])
        labels.extend([c.strip() for c in self.custom_allergens if c.strip()])
        return labels

    @property
    def primary_conditions(self) -> list[str]:
        return self.get_allergen_labels()

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
