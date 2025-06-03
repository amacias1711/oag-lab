# app/main.py

import uvicorn
from fastapi import FastAPI, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from app.utils.tracing import init_tracer, instrument_app
from app.core.config import settings
from app.api.auth import router as auth_router, JWTBearer

# routers públicos
from app.api.health     import router as health_router
# routers protegidos
from app.api.customers  import router as customers_router
from app.api.products   import router as products_router
from app.api.orders     import router as orders_router
from app.api.invoices   import router as invoices_router
from app.api.deliveries import router as deliveries_router
from app.api.payments   import router as payments_router

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

# 4.2 Protegidos (requieren JWT y rate-limit)
secure_deps = [
    Depends(JWTBearer()),              # valida el Bearer <token>
    Depends(limiter.limit("1/second;60/minute")) # apila rate-limit también (opcional porque default_limits ya aplica)
]

app.include_router(customers_router, dependencies=secure_deps)
app.include_router(products_router, dependencies=secure_deps)
app.include_router(orders_router, dependencies=secure_deps)
app.include_router(invoices_router, dependencies=secure_deps)
app.include_router(deliveries_router, dependencies=secure_deps)
app.include_router(payments_router, dependencies=secure_deps)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
