from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from proxy.auth import LicenseManager
from proxy.rate_limit import RateLimiter


def create_app(license_file: Path | None = None) -> FastAPI:
    if license_file is None:
        from proxy.config import LICENSE_FILE
        license_file = Path(LICENSE_FILE)

    license_mgr = LicenseManager(license_file)

    app = FastAPI(title="CR_BOT Proxy")
    app.state.license_mgr = license_mgr
    app.state.rate_limiter = RateLimiter(max_per_minute=10, max_per_day=50)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["POST"],
        allow_headers=["*"],
    )

    from proxy.routes.auth_routes import router as auth_router
    app.include_router(auth_router)

    from proxy.routes.transcribe_routes import router as transcribe_router
    app.include_router(transcribe_router)

    from proxy.routes.summarize_routes import router as summarize_router
    app.include_router(summarize_router)

    return app
