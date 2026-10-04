import time
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger("allerguard.sentry")

_sentry_initialized = False

def init_sentry():
    global _sentry_initialized
    if _sentry_initialized:
        return
    
    if settings.sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration

            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.sentry_environment,
                traces_sample_rate=1.0,
                integrations=[FastApiIntegration()],
                _experiments={"enable_metrics": True}
            )
            _sentry_initialized = True
            logger.info("Sentry Agent Tracing successfully initialized with 100% trace sampling.")
        except Exception as e:
            logger.warning(f"Failed to initialize Sentry: {e}")
    else:
        logger.info("Sentry DSN not provided. Agent tracing will record in local telemetry mode.")

class AgentSpan:
    """Agent span context manager for telemetry and Sentry tracing."""
    def __init__(self, op: str, description: str, data: Optional[Dict[str, Any]] = None):
        self.op = op
        self.description = description
        self.data = data or {}
        self.start_time = 0.0
        self.duration_ms = 0.0
        self._sentry_span = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        if _sentry_initialized:
            try:
                import sentry_sdk
                self._sentry_span = sentry_sdk.start_span(op=self.op, description=self.description)
                for k, v in self.data.items():
                    self._sentry_span.set_data(k, v)
                self._sentry_span.__enter__()
            except Exception:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000.0
        if self._sentry_span:
            try:
                self._sentry_span.set_data("duration_ms", round(self.duration_ms, 2))
                if exc_val:
                    self._sentry_span.set_status("internal_error")
                else:
                    self._sentry_span.set_status("ok")
                self._sentry_span.__exit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
        return False
