"""Standalone HTTP service for Zeerak feature agents."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .zeerak.agents import FeatureRunResult, run_feature_result
from .zeerak.config import FEATURE_OVERVIEW
from .zeerak.features import list_features, search_features
from .zeerak.formatting import OUTPUT_MODE_AUTO, OUTPUT_MODE_MARKDOWN, OUTPUT_MODE_PLAIN
from .zeerak.rendering import feature_to_dict
from .zeerak.routing import route_feature

load_dotenv()

OUTPUT_MODES = {OUTPUT_MODE_AUTO, OUTPUT_MODE_MARKDOWN, OUTPUT_MODE_PLAIN}


class HealthResponse(BaseModel):
    status: str
    service: str
    feature_count: int


class FeaturesResponse(BaseModel):
    features: list[dict[str, Any]]


class RouteRequest(BaseModel):
    task: str = Field(min_length=1)


class RouteResponse(BaseModel):
    feature: str
    reason: str


class FeatureRunRequest(BaseModel):
    feature: str = Field(min_length=1)
    task: str = Field(min_length=1)
    max_width: int | None = Field(default=None, gt=0)
    output_mode: str = OUTPUT_MODE_AUTO


class FeatureRunResponse(BaseModel):
    requested_feature: str
    feature: str
    model: str
    answer: str
    raw_answer: str
    structured: dict[str, Any] | None
    fallback_note: str | None
    route_reason: str | None


app = FastAPI(title="CustomAgentHF Service", version="0.1.0")


def _validate_feature(feature: str) -> None:
    if feature not in FEATURE_OVERVIEW:
        raise HTTPException(status_code=400, detail=f"Unsupported feature: {feature}")


def _validate_output_mode(output_mode: str) -> None:
    if output_mode not in OUTPUT_MODES:
        raise HTTPException(status_code=400, detail=f"Unsupported output_mode: {output_mode}")


def _serialize_run_result(result: FeatureRunResult) -> FeatureRunResponse:
    return FeatureRunResponse(
        requested_feature=result.requested_feature,
        feature=result.feature,
        model=result.model,
        answer=result.formatted_answer,
        raw_answer=result.raw_answer,
        structured=result.structured,
        fallback_note=result.fallback_note,
        route_reason=result.route_reason,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="customagenthf",
        feature_count=len(list_features(include_auto=False)),
    )


@app.get("/features", response_model=FeaturesResponse)
def features(
    query: str | None = Query(default=None),
    include_auto: bool = Query(default=False),
) -> FeaturesResponse:
    items = search_features(query, include_auto=include_auto) if query else list_features(include_auto=include_auto)
    return FeaturesResponse(features=[feature_to_dict(item) for item in items])


@app.post("/feature/route", response_model=RouteResponse)
def feature_route(payload: RouteRequest) -> RouteResponse:
    feature, reason = route_feature(payload.task)
    return RouteResponse(feature=feature, reason=reason)


@app.post("/feature/run", response_model=FeatureRunResponse)
def feature_run(payload: FeatureRunRequest) -> FeatureRunResponse:
    _validate_feature(payload.feature)
    _validate_output_mode(payload.output_mode)

    try:
        result = run_feature_result(
            payload.feature,
            payload.task,
            max_width=payload.max_width,
            output_mode=payload.output_mode,
        )
    except Exception as exc:  # pragma: no cover - exercised via patched tests and runtime integration
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return _serialize_run_result(result)


def main() -> None:
    import uvicorn

    host = os.getenv("CUSTOMAGENTHF_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("CUSTOMAGENTHF_SERVICE_PORT", "8001"))
    uvicorn.run("customagenthf.service:app", host=host, port=port)


if __name__ == "__main__":
    main()