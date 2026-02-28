# =============================================================
# NEXUS v5 — Pipeline Orchestrator
# Chains all 4 layers into a single end-to-end run.
# This is the "demo loop" shown in the competition presentation.
# =============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.project import ProjectInput 
from core.design_module       import GenerativeDesignModule
from core.digital_twin        import DigitalTwinEngine
from core.sensor_engine       import SensorEngine
from core.recalibration_engine import AdaptiveRecalibrationEngine
from core.impact_model        import ImpactModel


class NEXUSPipeline:
    """
    Full closed-loop pipeline:
    Brief → Generative Design → Digital Twin Sim → IoT Stream → Recalibration → Impact
    """

    def __init__(self):
        self.gdm    = GenerativeDesignModule()
        self.twin   = DigitalTwinEngine()
        self.sensor = SensorEngine()
        self.are    = AdaptiveRecalibrationEngine()
        self.impact = ImpactModel()

    def run(self, project: ProjectInput, verbose: bool = True) -> dict:
        project.validate()
        ctx = project.to_prompt_context()

        self._header("NEXUS v5 — Dynamic Engineering System | L&T CreaTech '26")
        self._step("STEP 1 — Generative Design")

        # ── Layer 1: Generate design variants ─────────────────
        variants = self.gdm.generate_variants(project)
        recommended = min(variants, key=lambda v: v["risk_score"])

        if verbose:
            for v in variants:
                print(
                    f"  [{v['id']}] {v['name']} | "
                    f"Depth: {v['depth_m']}m | Piles: {v['piles']} | "
                    f"Risk: {v['risk_score']}/10 | Cost: ₹{v['cost_cr']} Cr"
                )
            print(f"\n  ⭐  Recommended: {recommended['id']} — {recommended['name']}")

        # ── Layer 2: Digital Twin simulation ──────────────────
        self._step("STEP 2 — Digital Twin Simulation (Monte Carlo)")
        sim = self.twin.simulate(project_context=ctx)
        if verbose:
            print(sim.summary())

        # ── Layer 3: IoT sensor stream ─────────────────────────
        self._step("STEP 3 — IoT Sensor Stream (Live Site Data)")
        stream = self.sensor.simulate_stream(design_sbc=180.0)

        if verbose:
            recent = stream.readings[-5:]
            print(f"  Last 5 readings: {[r.sbc_kNm2 for r in recent]} kN/m²")
            print(f"  {stream.summary()}")

        # ── Layer 4: Adaptive Recalibration ───────────────────
        patch = None
        if stream.trigger_recal:
            self._step("STEP 4 — ADAPTIVE RECALIBRATION ENGINE TRIGGERED")
            patch = self.are.generate_patch(
                deviation_percent = stream.deviation_percent,
                project_context   = ctx,
                current_variant   = recommended,
                budget_cr         = project.budget_cr,
            )
            if verbose:
                print(patch.summary())

        # ── Business Impact ───────────────────────────────────
        self._step("STEP 5 — Business Impact Calculation")
        impact = self.impact.calculate(sim.failure_probability, project.budget_cr)
        if verbose:
            print(impact.summary())

        return {
            "project":     project,
            "variants":    variants,
            "recommended": recommended,
            "simulation":  sim,
            "sensor":      stream,
            "patch":       patch,
            "impact":      impact,
        }

    # ── Helpers ───────────────────────────────────────────────
    @staticmethod
    def _header(text: str):
        print(f"\n{'═'*60}")
        print(f"  {text}")
        print(f"{'═'*60}\n")

    @staticmethod
    def _step(text: str):
        print(f"\n{'─'*60}")
        print(f"  {text}")
        print(f"{'─'*60}")


# =============================================================
# DEMO ENTRY POINT
# =============================================================

if __name__ == "__main__":
    project = ProjectInput(
        project_id   = "LNT-HYD-2026-001",
        structure    = "10-storey Residential Tower",
        soil_type    = "Black Cotton Soil",
        seismic_zone = "III",
        load_kN      = 2500.0,
        budget_cr    = 12.5,
        season       = "Monsoon",
        location     = "Hyderabad, Telangana",
        vertical     = "Buildings & Factories",
        notes        = "Adjacent to water body; high water table expected.",
    )

    pipeline = NEXUSPipeline()
    result   = pipeline.run(project, verbose=True)
