from dataclasses import dataclass
from typing import Optional


@dataclass
class ProjectInput:
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

    def validate(self):
        errors = []
        if self.load_kN <= 0:
            errors.append("load_kN must be positive")
        if self.budget_cr <= 0:
            errors.append("budget_cr must be positive")
        if self.seismic_zone not in ("II", "III", "IV", "V"):
            errors.append(f"seismic_zone must be II/III/IV/V, got {self.seismic_zone}")
        if errors:
            raise ValueError("ProjectInput validation failed: " + "; ".join(errors))
        return True

    def to_prompt_context(self) -> str:
        return (
            f"Project: {self.project_id} | Structure: {self.structure}\n"
            f"Soil: {self.soil_type} | Seismic Zone: {self.seismic_zone}\n"
            f"Load: {self.load_kN} kN | Budget: ₹{self.budget_cr} Cr\n"
            f"Season: {self.season} | Location: {self.location}\n"
            f"L&T Vertical: {self.vertical}"
            + (f"\nEngineer Notes: {self.notes}" if self.notes else "")
        )