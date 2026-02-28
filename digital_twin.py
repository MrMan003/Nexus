# =============================================================
# NEXUS v5 — Layer 2: Digital Twin & Predictive Simulation
# Monte Carlo engine + Gemini risk narrative
# =============================================================

import numpy as np
from dataclasses import dataclass
from config import MC_ITERATIONS, SBC_DEFAULT_MEAN, SBC_DEFAULT_STD
from utils.gemini_client import call_gemini


@dataclass
class SimulationResult:
    failure_probability:  float   # % of runs where SF < 1.0
    marginal_probability: float   # % of runs where 1.0 ≤ SF < 1.5
    safe_probability:     float   # % of runs where SF ≥ 1.5
    mean_sf:              float   # mean safety factor
    p5_sf:                float   # 5th percentile SF (worst 5% of scenarios)
    p95_sf:               float   # 95th percentile SF
    risk_band:            str     # LOW / MODERATE / HIGH / CRITICAL
    gemini_narrative:     str = ""

    def summary(self) -> str:
        return (
            f"Safety Factor → Mean: {self.mean_sf}  |  P5: {self.p5_sf}  |  P95: {self.p95_sf}\n"
            f"Failure Probability: {self.failure_probability}%\n"
            f"Risk Band: {self.risk_band}\n"
            + (f"AI Analysis: {self.gemini_narrative}" if self.gemini_narrative else "")
        )


class DigitalTwinEngine:
    """
    Runs Monte Carlo simulation over soil bearing capacity
    vs. structural demand to produce probabilistic risk scores.

    Can be seeded with real geotechnical report values.
    """

    def simulate(
        self,
        mean_sbc:  float = SBC_DEFAULT_MEAN,
        std_sbc:   float = SBC_DEFAULT_STD,
        mean_demand: float = 165.0,
        std_demand:  float = 10.0,
        n:           int   = MC_ITERATIONS,
        project_context: str = "",
        use_gemini: bool = True,
    ) -> SimulationResult:

        rng = np.random.default_rng(seed=42)   # reproducible for demo
        soil   = rng.normal(mean_sbc,    std_sbc,    n)
        demand = rng.normal(mean_demand, std_demand, n)

        sf = soil / demand

        failure_prob  = float(np.mean(sf <  1.0) * 100)
        marginal_prob = float(np.mean((sf >= 1.0) & (sf < 1.5)) * 100)
        safe_prob     = float(np.mean(sf >= 1.5) * 100)
        mean_sf       = float(np.mean(sf))
        p5            = float(np.percentile(sf, 5))
        p95           = float(np.percentile(sf, 95))

        risk_band = (
            "CRITICAL" if failure_prob > 10 else
            "HIGH"     if failure_prob >  5 else
            "MODERATE" if failure_prob >  2 else
            "LOW"
        )

        narrative = ""
        if use_gemini and project_context:
            narrative = self._gemini_narrative(
                failure_prob, marginal_prob, mean_sf, p5, risk_band, project_context
            )

        return SimulationResult(
            failure_probability  = round(failure_prob, 2),
            marginal_probability = round(marginal_prob, 2),
            safe_probability     = round(safe_prob, 2),
            mean_sf              = round(mean_sf, 3),
            p5_sf                = round(p5, 3),
            p95_sf               = round(p95, 3),
            risk_band            = risk_band,
            gemini_narrative     = narrative,
        )

    def _gemini_narrative(
        self, failure_prob, marginal_prob, mean_sf, p5, risk_band, project_context
    ) -> str:
        prompt = f"""
You are a structural risk analyst at L&T India.
Interpret these Monte Carlo simulation results for the project team.

PROJECT CONTEXT:
{project_context}

SIMULATION RESULTS:
- Failure probability (SF < 1.0): {failure_prob}%
- Marginal probability (1.0 ≤ SF < 1.5): {marginal_prob}%
- Mean safety factor: {mean_sf}
- Worst-case 5th percentile SF: {p5}
- Risk band: {risk_band}

In 3 technical sentences:
1. What does this probability mean for the project?
2. What is the primary driver of risk?
3. What mitigation should the engineer take before breaking ground?
"""
        try:
            return call_gemini(prompt, fast=True)
        except Exception:
            return (
                f"Risk band is {risk_band}. "
                f"Safety factor mean of {mean_sf:.2f} with {failure_prob:.1f}% failure probability. "
                "Review geotechnical report and increase founding depth if SF < 1.5."
            )
