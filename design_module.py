# =============================================================
# NEXUS v5 — Layer 1: Generative Design Module (GDM)
# Gemini generates IS-code-compliant design variants.
# Falls back to deterministic engine if Gemini unavailable.
# =============================================================

from core.project import ProjectInput
from utils.gemini_client import call_gemini_json
from config import IS_CODES


class GenerativeDesignModule:
    """
    Entry point for NEXUS.
    Input: ProjectInput brief
    Output: 3-5 ranked structural design variants (JSON)
    """

    def generate_variants(self, project: ProjectInput) -> list[dict]:
        """
        Primary path: Gemini generates contextual variants.
        Fallback: deterministic rule engine.
        """
        try:
            return self._gemini_variants(project)
        except Exception as e:
            print(f"[GDM] Gemini unavailable ({e}). Using deterministic engine.")
            return self._deterministic_variants(project)

    # ── Gemini Path ────────────────────────────────────────────
    def _gemini_variants(self, project: ProjectInput) -> list[dict]:
        prompt = f"""
You are a senior structural engineer at Larsen & Toubro India.
Generate exactly 3 foundation design variants for this project brief.
Apply relevant IS codes: {IS_CODES['foundation']}, {IS_CODES['seismic']}.

PROJECT BRIEF:
{project.to_prompt_context()}

Return a JSON ARRAY of exactly 3 objects. Each object must have:
- id           : "V1", "V2", "V3"
- name         : short descriptive name (e.g. "Cost-Optimised Raft")
- foundation_type : type (Raft / Pile / Strip / Combined)
- depth_m      : founding depth in meters (float)
- piles        : number of piles (0 if not applicable)
- width_m      : footing width in meters (float)
- risk_score   : float 1-10 (10 = highest risk)
- cost_cr      : estimated cost in Indian Crore (float)
- is_code_refs : list of relevant IS codes applied
- rationale    : one sentence explaining the trade-off
"""
        variants = call_gemini_json(prompt)

        # Validate structure
        required = {"id", "name", "depth_m", "piles", "risk_score", "cost_cr"}
        for v in variants:
            missing = required - set(v.keys())
            if missing:
                raise ValueError(f"Variant {v.get('id')} missing keys: {missing}")

        return variants

    # ── Deterministic Fallback ─────────────────────────────────
    def _deterministic_variants(self, project: ProjectInput) -> list[dict]:
        soil_factor = (
            1.3 if "black" in project.soil_type.lower() else
            1.1 if "sand"  in project.soil_type.lower() else
            1.0
        )
        seismic_factor = {"II": 1.0, "III": 1.1, "IV": 1.2, "V": 1.35}.get(
            project.seismic_zone, 1.0
        )
        base_depth = 2.0 * soil_factor * seismic_factor

        return [
            {
                "id": "V1", "name": "Cost-Optimised Shallow",
                "foundation_type": "Raft",
                "depth_m": round(base_depth, 2), "piles": 0,
                "width_m": round(base_depth * 1.5, 2),
                "risk_score": 6.5,
                "cost_cr": round(project.budget_cr * 0.82, 2),
                "is_code_refs": [IS_CODES["foundation"]],
                "rationale": "Lowest cost; acceptable for low seismic & stable soil."
            },
            {
                "id": "V2", "name": "Balanced — Recommended",
                "foundation_type": "Combined Raft + Piles",
                "depth_m": round(base_depth + 0.4, 2), "piles": 4,
                "width_m": round(base_depth * 1.8, 2),
                "risk_score": 3.8,
                "cost_cr": round(project.budget_cr, 2),
                "is_code_refs": [IS_CODES["foundation"], IS_CODES["seismic"]],
                "rationale": "Best cost-safety balance for Indian conditions."
            },
            {
                "id": "V3", "name": "Safety-Maximised Pile",
                "foundation_type": "Bored Cast-in-Situ Piles",
                "depth_m": round(base_depth + 0.8, 2), "piles": 8,
                "width_m": round(base_depth * 2.0, 2),
                "risk_score": 1.5,
                "cost_cr": round(project.budget_cr * 1.28, 2),
                "is_code_refs": [IS_CODES["foundation"], IS_CODES["seismic"], IS_CODES["concrete"]],
                "rationale": "Maximum safety margin; recommended for Zone IV/V or poor soil."
            },
        ]

    def explain_recommendation(self, variants: list[dict], project: ProjectInput) -> str:
        """
        Gemini explains which variant to pick and why,
        in plain English for the site engineer.
        """
        try:
            prompt = f"""
You are a structural engineering advisor at L&T.
A site engineer needs your recommendation.

PROJECT: {project.to_prompt_context()}

VARIANTS GENERATED:
{variants}

In 3-4 concise sentences:
1. Which variant do you recommend and why?
2. What is the key risk to watch out for on site?
3. Any IS code clause the engineer must verify?
"""
            return call_gemini_json.__module__ and __import__(
                "utils.gemini_client", fromlist=["call_gemini"]
            ).call_gemini(prompt, fast=True)
        except Exception:
            rec = min(variants, key=lambda v: v["risk_score"])
            return (
                f"Recommended variant: {rec['id']} — {rec['name']}. "
                f"Risk score: {rec['risk_score']}/10. "
                f"Cost: ₹{rec['cost_cr']} Cr. "
                "Verify soil bearing capacity on-site before finalising."
            )
