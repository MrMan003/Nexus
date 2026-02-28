# =============================================================
# NEXUS v5 — Configuration & Constants
# L&T CreaTech '26 | Problem Statement 3
# =============================================================

import os

# ── Gemini Model Config ────────────────────────────────────────
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_FLASH = "gemini-2.0-flash"

# ── API Key (set via env or pass directly) ─────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

# ── Sensor Thresholds ──────────────────────────────────────────
DEVIATION_CRITICAL = 20.0   # %  → emergency recalibration
DEVIATION_MODERATE  = 10.0   # %  → standard recalibration
DEVIATION_MINOR     =  5.0   # %  → log + monitor

# ── Monte Carlo Simulation ─────────────────────────────────────
MC_ITERATIONS = 1000
SBC_DEFAULT_MEAN = 180      # kN/m²
SBC_DEFAULT_STD  =  25

# ── IS Code Reference Tags (used in Gemini prompts) ───────────
IS_CODES = {
    "foundation": "IS 1080, IS 6403",
    "seismic":    "IS 1893 (Part 1)",
    "concrete":   "IS 456:2000",
    "loading":    "IS 875 (Parts 1-5)",
}

# ── IoT Sensor Simulation Defaults ────────────────────────────
SENSOR_TOTAL_READINGS   = 20
SENSOR_DEVIATION_START  = 12   # reading index at which soil degrades
