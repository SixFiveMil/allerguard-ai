import time
import logging
from typing import Dict, Any, Optional

from app.config import settings
from app.core.sentry_tracing import AgentSpan
from app.core.tabpfn_classifier import tabpfn_classifier
from app.core.gemma_engine import gemma_engine
from app.core.serpapi_tool import serpapi_tool
from app.core.elevenlabs_tool import elevenlabs_tool

logger = logging.getLogger("allerguard.agent")

class AllerGuardAgent:
    """
    AllerGuard AI Master Orchestrator Agent.
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
        certified_gf: bool = False
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        trace_steps = []

        with AgentSpan("agent.workflow", f"AllerGuard analysis: {product_name}") as master_span:
            # 1. TabPFN Inference
            step1_start = time.perf_counter()
            tabpfn_res = tabpfn_classifier.predict(
                raw_text=ingredients_text,
                category=category,
                dedicated_facility=dedicated_facility,
                certified_gf=certified_gf
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
                web_search_results=web_res
            )
            step3_duration = round((time.perf_counter() - step3_start) * 1000, 2)
            trace_steps.append({
                "step": 3,
                "name": f"Google Gemma 2 ({gemma_res['execution_mode']})",
                "operation": "gemma.inference",
                "details": f"Generated clinical dietary safety synthesis for {settings.friend.name}",
                "latency_ms": step3_duration
            })

            # 4. ElevenLabs Voice Generation
            step4_start = time.perf_counter()
            audio_script = (
                f"{settings.friend.name}, AllerGuard safety assessment for {product_name}: "
                f"Verdict is {tabpfn_res['risk_level']}. "
                f"{'Danger! Do not eat this item.' if tabpfn_res['risk_level'] == 'DANGER' else 'Exercise caution due to ambiguous ingredients.' if tabpfn_res['risk_level'] == 'CAUTION' else 'This product meets your safe dietary profile.'}"
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
            master_span.data["risk_level"] = tabpfn_res["risk_level"]

            return {
                "product_name": product_name,
                "friend_name": settings.friend.name,
                "conditions": settings.friend.primary_conditions,
                "verdict": tabpfn_res["risk_level"],
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
