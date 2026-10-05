import time
import logging
from typing import Dict, Any, Optional, List

from app.config import settings, ALLERGEN_REGISTRY
from app.core.sentry_tracing import AgentSpan
from app.core.tabpfn_classifier import tabpfn_classifier
from app.core.gemma_engine import gemma_engine
from app.core.serpapi_tool import serpapi_tool
from app.core.elevenlabs_tool import elevenlabs_tool

logger = logging.getLogger("allerguard.agent")

class AllerGuardAgent:
    """
    AllerGuard AI Master Orchestrator Agent.
    Customized specifically for Tree Nut, Peanut, Coconut, and Sesame allergies.
    Combines:
    - Prior Labs TabPFN (Tabular risk classification)
    - Google Gemma 2 (Open-weight clinical reasoning)
    - SerpApi (Live recall and FDA verification)
    - ElevenLabs (Hands-free voice accessibility)
    - Sentry (Agent Tracing & Telemetry)
    """

    async def analyze_product(
        self,
        product_name: str,
        ingredients_text: str,
        category: str = "general",
        dedicated_facility: bool = False,
        certified_allergen_free: bool = False,
        user_name: Optional[str] = None,
        selected_allergens: Optional[List[str]] = None,
        custom_allergens: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        trace_steps = []

        name = user_name or settings.profile.name
        
        # Build active triggers and labels based on request or global profile
        if selected_allergens is not None:
            active_allergens = selected_allergens
            active_custom = custom_allergens or []
            triggers = []
            labels = []
            for k in active_allergens:
                if k in ALLERGEN_REGISTRY:
                    triggers.extend(ALLERGEN_REGISTRY[k]["triggers"])
                    labels.append(ALLERGEN_REGISTRY[k]["label"])
            triggers.extend([c.lower().strip() for c in active_custom if c.strip()])
            labels.extend([c.strip() for c in active_custom if c.strip()])
            triggers = list(set(triggers))
        else:
            triggers = settings.profile.get_all_triggers()
            labels = settings.profile.get_allergen_labels()

        with AgentSpan("agent.workflow", f"AllerGuard analysis: {product_name}") as master_span:
            # 1. TabPFN Inference
            step1_start = time.perf_counter()
            tabpfn_res = tabpfn_classifier.predict(
                raw_text=ingredients_text,
                category=category,
                dedicated_facility=dedicated_facility,
                certified_allergen_free=certified_allergen_free,
                active_triggers=triggers
            )
            step1_duration = round((time.perf_counter() - step1_start) * 1000, 2)
            trace_steps.append({
                "step": 1,
                "name": "TabPFN Tabular Foundation Model",
                "operation": "tabpfn.classify",
                "details": f"Predicted {tabpfn_res['risk_level']} (Safe: {tabpfn_res['probabilities']['safe']}%, Caution: {tabpfn_res['probabilities']['caution']}%, Danger: {tabpfn_res['probabilities']['danger']}%)",
                "latency_ms": step1_duration
            })

            # 2. SerpApi Live Web Verification
            step2_start = time.perf_counter()
            search_query = f"{product_name} {category}".strip()
            web_res = await serpapi_tool.search_recall_and_brand_safety(search_query)
            step2_duration = round((time.perf_counter() - step2_start) * 1000, 2)
            trace_steps.append({
                "step": 2,
                "name": "SerpApi Live Food Safety Search",
                "operation": "serpapi.search",
                "details": f"Retrieved {len(web_res.get('findings', []))} intelligence findings from {web_res.get('source')}",
                "latency_ms": step2_duration
            })

            # 3. Open-weight Gemma 2 Reasoning
            step3_start = time.perf_counter()
            gemma_res = await gemma_engine.analyze(
                product_name=product_name,
                ingredients_text=ingredients_text,
                tabpfn_results=tabpfn_res,
                web_search_results=web_res,
                user_name=name,
                allergen_labels=labels
            )
            step3_duration = round((time.perf_counter() - step3_start) * 1000, 2)
            trace_steps.append({
                "step": 3,
                "name": f"Google Gemma 2 ({gemma_res['execution_mode']})",
                "operation": "gemma.inference",
                "details": f"Generated clinical dietary safety synthesis for {name}",
                "latency_ms": step3_duration
            })

            # 4. ElevenLabs Voice Generation
            step4_start = time.perf_counter()
            labels_summary = ", ".join(labels[:3])
            audio_script = (
                f"{name}, AllerGuard safety assessment for {product_name}: "
                f"Verdict is {tabpfn_res['risk_level']}. "
                f"{'Danger! Do not eat this item. Critical allergen detected.' if tabpfn_res['risk_level'] == 'DANGER' else f'Caution! Ambiguous ingredients may hide {labels_summary} derivatives.' if tabpfn_res['risk_level'] == 'CAUTION' else f'This product meets your dietary profile with no detected {labels_summary} allergens.'}"
            )
            voice_res = await elevenlabs_tool.generate_speech(audio_script)
            step4_duration = round((time.perf_counter() - step4_start) * 1000, 2)
            trace_steps.append({
                "step": 4,
                "name": "ElevenLabs Voice Accessibility",
                "operation": "elevenlabs.tts",
                "details": f"Synthesized hands-free safety briefing using {voice_res['engine']}",
                "latency_ms": step4_duration
            })

            total_duration = round((time.perf_counter() - start_time) * 1000, 2)
            master_span.data["total_latency_ms"] = total_duration

            # Contextual Synthesis:
            # TabPFN provides the statistical risk prior, but Gemma 2 provides contextual language understanding
            # (e.g. recognizing that "nut-free" or "sesame-free" is a safety claim, not an active ingredient).
            gemma_text = gemma_res.get("analysis", "")
            final_verdict = tabpfn_res["risk_level"]
            if "[SAFE]" in gemma_text:
                final_verdict = "SAFE"
            elif "[DANGER" in gemma_text:
                final_verdict = "DANGER"
            elif "[CAUTION" in gemma_text:
                final_verdict = "CAUTION"

            master_span.data["risk_level"] = final_verdict

            return {
                "product_name": product_name,
                "user_name": name,
                "conditions": labels,
                "verdict": final_verdict,
                "tabpfn": tabpfn_res,
                "web_grounding": web_res,
                "gemma_analysis": gemma_res,
                "voice_guidance": voice_res,
                "telemetry": {
                    "total_latency_ms": total_duration,
                    "traces": trace_steps,
                    "sentry_tracked": bool(settings.sentry_dsn)
                }
            }

allerguard_agent = AllerGuardAgent()
