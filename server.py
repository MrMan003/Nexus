# =============================================================
# NEXUS v5 — REST API Layer (FastAPI)
# Exposes the pipeline as HTTP endpoints.
# For demo: run with `uvicorn api.server:app --reload`
# =============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.project              import ProjectInput
from core.design_module        import GenerativeDesignModule
from core.digital_twin         import DigitalTwinEngine
from core.sensor_engine        import SensorEngine
from core.recalibration_engine import AdaptiveRecalibrationEngine
from core.impact_model         import ImpactModel

app = FastAPI(
    title="NEXUS v5 — AI Dynamic Engineering System",
    description="L&T CreaTech '26 | Problem Statement 3 | Real-time Generative Design + Recalibration",
    version="5.0",
)

# ── Request/Response Models ────────────────────────────────────

class ProjectRequest(BaseModel):
    project_id:   str
    structure:    str
    soil_type:    str
    seismic_zone: str
    load_kN:      float
    budget_cr:    float
    season:       str
    location:     str = "India"
    vertical:     str = "Buildings"
    notes:        Optional[str] = None


class SensorRequest(BaseModel):
    design_sbc:      float = 180.0
    readings:        Optional[list[float]] = None  # real readings; None = simulate


# ── Endpoints ─────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "NEXUS operational", "version": "5.0"}


@app.post("/design/variants")
def generate_variants(req: ProjectRequest):
    """Layer 1 — Generate 3 IS-code-compliant design variants."""
    p = _to_project(req)
    try:
        p.validate()
    except ValueError as e:
        raise HTTPException(400, str(e))
    gdm = GenerativeDesignModule()
    variants = gdm.generate_variants(p)
    recommendation = gdm.explain_recommendation(variants, p)
    return {"variants": variants, "recommendation": recommendation}


@app.post("/simulate/twin")
def run_digital_twin(req: ProjectRequest):
    """Layer 2 — Monte Carlo digital twin simulation."""
    p = _to_project(req)
    twin = DigitalTwinEngine()
    result = twin.simulate(project_context=p.to_prompt_context())
    return {
        "failure_probability":  result.failure_probability,
        "marginal_probability": result.marginal_probability,
        "safe_probability":     result.safe_probability,
        "mean_sf":              result.mean_sf,
        "p5_sf":                result.p5_sf,
        "risk_band":            result.risk_band,
        "narrative":            result.gemini_narrative,
    }


@app.post("/sensor/stream")
def sensor_stream(req: SensorRequest):
    """Layer 3 — IoT sensor stream analysis."""
    engine = SensorEngine()
    if req.readings:
        result = SensorEngine.ingest_real_readings(req.readings, req.design_sbc)
    else:
        result = engine.simulate_stream(design_sbc=req.design_sbc)
    return {
        "deviation_detected": result.deviation_detected,
        "deviation_percent":  result.deviation_percent,
        "alert_level":        result.alert_level,
        "trigger_recal":      result.trigger_recal,
        "last_5_readings":    [r.sbc_kNm2 for r in result.readings[-5:]],
    }


@app.post("/recalibrate")
def recalibrate(
    deviation_percent: float,
    budget_cr: float = 10.0,
    project_id: str = "unknown",
):
    """Layer 4 — Adaptive Recalibration Engine. Core innovation endpoint."""
    are = AdaptiveRecalibrationEngine()
    patch = are.generate_patch(deviation_percent=deviation_percent, budget_cr=budget_cr)
    return {
        "severity":          patch.severity,
        "structural_action": patch.structural_action,
        "add_depth_mm":      patch.add_depth_mm,
        "add_piles":         patch.add_piles,
        "cost_delta_cr":     patch.cost_delta_cr,
        "new_risk_band":     patch.new_risk_band,
        "rationale":         patch.gemini_rationale,
        "site_instructions": patch.site_instructions,
        "requires_approval": patch.requires_approval,
    }


@app.post("/impact")
def business_impact(failure_prob: float, budget_cr: float):
    """Business Impact Model — ROI quantification for L&T leadership."""
    model  = ImpactModel()
    report = model.calculate(failure_prob, budget_cr)
    return {
        "rework_saving_cr":      report.rework_saving_cr,
        "delay_saving_cr":       report.delay_saving_cr,
        "design_saving_cr":      report.design_time_saving_cr,
        "total_saving_cr":       report.total_saving_cr,
        "roi_multiplier":        report.roi_multiplier,
        "payback_months":        report.payback_months,
    }


# ── Helper ────────────────────────────────────────────────────

def _to_project(req: ProjectRequest) -> ProjectInput:
    return ProjectInput(
        project_id   = req.project_id,
        structure    = req.structure,
        soil_type    = req.soil_type,
        seismic_zone = req.seismic_zone,
        load_kN      = req.load_kN,
        budget_cr    = req.budget_cr,
        season       = req.season,
        location     = req.location,
        vertical     = req.vertical,
        notes        = req.notes,
    )
