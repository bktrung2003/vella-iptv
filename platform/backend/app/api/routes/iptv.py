"""IPTV / in-room TV kiosk — control plane only (video stays on the HLS gateway)."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter(prefix="/iptv", tags=["iptv"])


class TvBootstrap(BaseModel):
    """Discovery payload for browser kiosk on the property VLAN."""

    schema_version: Literal["0.1"] = "0.1"
    gateway_hls_base_url: str | None = Field(
        default=None,
        description="Base URL for HLS from the property gateway (HTTP), not this API.",
    )


class TvHealth(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["vella-iptv-control-plane"] = "vella-iptv-control-plane"


@router.get("/bootstrap", response_model=TvBootstrap)
def tv_bootstrap() -> TvBootstrap:
    """
    Called by the in-room TV web client on load.

    MVP: no auth. Later: device or room-scoped token and per-property config from DB.
    """
    return TvBootstrap(gateway_hls_base_url=settings.IPTV_GATEWAY_HLS_BASE_URL)


@router.get("/health", response_model=TvHealth)
def tv_health() -> TvHealth:
    """Probe for TV clients or property monitoring."""
    return TvHealth()
