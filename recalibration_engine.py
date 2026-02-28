# =============================================================
# NEXUS v5 — Layer 4: Adaptive Recalibration Engine (ARE)
# THE CORE INNOVATION: deviation-triggered design auto-correction
# Gemini generates the structural rationale + patch instructions
# =============================================================

from dataclasses import dataclass
from utils.gemini_client import call_gemini, call_gemini_json
from config import IS_CODES, DEVIATION_CRITICAL, DEVIATION_MODERATE


@dataclass
class RecalibrationPatch:
    deviation_percent:   float
    severity:            str         # CRITICAL / MODERATE / MINOR
    structural_action:   str         # what to change (depth, piles, etc.)
    add_depth_mm:        int
    add_piles:           int
    new_risk_band:       str         # projected risk after patch
    cost_delta_cr:       float       # additional cost in Crore
    is_code_reference:   str
    gemini_rationale:    str = ""    # AI-generated engineering explanation
    site_instructions:   str = ""    # Plain-English field instructions
    requires_approval:   bool = True

    def summary(self) -> str:
        return (
            f"[{self.severity}] Deviation: {self.deviation_percent:.1f}%\n"
            f"Action: {self.structural_action}\n"
            f"IS Code: {self.is_code_reference}\n"
            f"Projected Risk: {self.new_risk_band} | Cost Delta: +₹{self.cost_delta_cr} Cr\n"
            + (f"Rationale: {self.gemini_rationale}\n" if self.gemini_rationale else "")
            + (f"Site Instructions: {self.site_instructions}" if self.site_instructions else "")
        )


class AdaptiveRecalibrationEngine:
    """
    Listens for SensorStreamResult deviation triggers.
    When threshold is crossed → generates a RecalibrationPatch.

    This is NEXUS's globally-differentiating feature:
    no existing tool auto-generates design corrections
    in response to live site sensors.
    """

    def generate_patch(
        self,
        deviation_percent: float,
        project_context:   str = "",
        current_variant:   dict = None,
        budget_cr:         float = 10.0,
    ) -> RecalibrationPatch:

        # ── Determine base action ──────────────────────────────
        if deviation_percent > DEVIATION_CRITICAL:
            severity       = "CRITICAL"
            add_depth_mm   = 600
            add_piles      = 4
            new_risk_band  = "LOW"
            cost_delta_pct = 0.18
            action         = (
                f"Increase founding depth by {600}mm. "
                f"Add {4} bored cast-in-situ piles per column. "
                "Perform additional plate load test per IS 1888."
            )
        elif deviation_percent > DEVIATION_MODERATE:
            severity       = "MODERATE"
            add_depth_mm   = 350
            add_piles      = 2
            new_risk_band  = "MODERATE"
            cost_delta_pct = 0.09
            action         = (
                f"Increase founding depth by {350}mm. "
                f"Add {2} piles for load redistribution. "
                "Recheck SBC with dynamic cone penetration test."
            )
        else:
            severity       = "MINOR"
            add_depth_mm   = 150
            add_piles      = 0
            new_risk_band  = "LOW-MODERATE"
            cost_delta_pct = 0.03
            action         = (
                "Increase reinforcement grade from Fe415 to Fe500. "
                "Add 150mm to footing depth as precaution."
            )

        cost_delta = round(budget_cr * cost_delta_pct, 2)

        # ── Gemini Path: get engineering rationale + site instructions ──
        rationale, site_instr = self._gemini_explanations(
            deviation_percent, action, severity, project_context, current_variant
        )

        return RecalibrationPatch(
            deviation_percent  = round(deviation_percent, 2),
            severity           = severity,
            structural_action  = action,
            add_depth_mm       = add_depth_mm,
            add_piles          = add_piles,
            new_risk_band      = new_risk_band,
            cost_delta_cr      = cost_delta,
            is_code_reference  = f"{IS_CODES['foundation']}; {IS_CODES['seismic']}",
            gemini_rationale   = rationale,
            site_instructions  = site_instr,
            requires_approval  = severity in ("CRITICAL", "MODERATE"),
        )

    def _gemini_explanations(
        self,
        deviation_percent: float,
        action: str,
        severity: str,
        project_context: str,
        current_variant: dict,
    ) -> tuple[str, str]:
        """
        Returns (rationale, site_instructions) from Gemini.
        Falls back to deterministic strings if Gemini fails.
        """
        try:
            prompt = f"""
You are a senior structural engineer at L&T doing an emergency site review.

SITUATION:
IoT soil sensors have detected that actual soil bearing capacity (SBC) has 
dropped {deviation_percent:.1f}% below the design assumption.
Severity classification: {severity}

PROJECT CONTEXT:
{project_context}

CURRENT DESIGN:
{current_variant or "Not provided"}

PROPOSED STRUCTURAL FIX:
{action}

Provide two things:
1. RATIONALE (3 technical sentences): Why this drop in SBC is structurally 
   dangerous and why the proposed fix addresses it per IS codes.
2. SITE_INSTRUCTIONS (2 sentences): Plain-English instructions the site 
   engineer can relay to the foreperson immediately.

Return as JSON:
{{"rationale": "...", "site_instructions": "..."}}
"""
            result = call_gemini_json(prompt, fast=True)
            return result.get("rationale", ""), result.get("site_instructions", "")

        except Exception:
            return (
                f"A {deviation_percent:.1f}% SBC drop reduces the safety factor below acceptable IS code limits. "
                "The proposed depth increase and pile addition restore the required bearing capacity per IS 6403. "
                "Immediate implementation prevents potential differential settlement and structural distress.",
                f"Stop all foundation work. Contact the structural engineer. "
                f"Implement '{action}' before resuming.",
            )
