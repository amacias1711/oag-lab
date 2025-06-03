# app/main.py

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from app.utils.tracing import init_tracer, instrument_app
from app.core.config import settings
from app.api.auth import router as auth_router

# routers públicos
from app.api.health import router as health_router

app = FastAPI(title="API Gateway SBO ↔ Odoo")

# 1) OpenTelemetry (Jaeger) – opcional
init_tracer()
instrument_app(app)

# 2) Prometheus metrics
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, include_in_schema=True)

# 3) Rate limiting (global: 10 requests/minuto por IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# 4) Routers
# 4.1 Públicos (no requieren token)
app.include_router(health_router)      # /api/health
app.include_router(auth_router)        # /api/token

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
