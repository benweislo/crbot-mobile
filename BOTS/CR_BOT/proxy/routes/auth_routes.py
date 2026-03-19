from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class ValidateRequest(BaseModel):
    license_key: str


@router.post("/auth/validate")
async def validate_license(req: ValidateRequest, request: Request):
    mgr = request.app.state.license_mgr
    result = mgr.validate(req.license_key)
    return result
