from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from proxy.auth import LicenseManager


def create_app(license_file: Path | None = None) -> FastAPI:
    if license_file is None:
        from proxy.config import LICENSE_FILE
        license_file = Path(LICENSE_FILE)

    license_mgr = LicenseManager(license_file)

    app = FastAPI(title="CR_BOT Proxy")
    app.state.license_mgr = license_mgr

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["POST"],
        allow_headers=["*"],
    )

    from proxy.routes.auth_routes import router as auth_router
    app.include_router(auth_router)

    return app
