# NEXUS v5 — AI Dynamic Engineering System
### L&T CreaTech '26 | Problem Statement 3 | Gemini-Powered

---

## Architecture (4-Layer Closed Loop)

```
[PROJECT BRIEF]
      │
      ▼
┌─────────────────────────────────────┐
│  LAYER 1: Generative Design Module  │  ← Gemini generates IS-code variants
│  GenerativeDesignModule             │
└──────────────────┬──────────────────┘
                   │  3 design variants (ranked by risk + cost)
                   ▼
┌─────────────────────────────────────┐
│  LAYER 2: Digital Twin Engine       │  ← Monte Carlo simulation (1000 runs)
│  DigitalTwinEngine                  │    Gemini explains risk narrative
└──────────────────┬──────────────────┘
                   │  risk_band + safety factor distribution
                   ▼
┌─────────────────────────────────────┐
│  LAYER 3: IoT Sensor Engine         │  ← Live soil SBC stream
│  SensorEngine                       │    Anomaly detection + alert levels
└──────────────────┬──────────────────┘
                   │  deviation_percent → triggers recalibration
                   ▼
┌─────────────────────────────────────┐
│  LAYER 4: Adaptive Recalibration    │  ← CORE INNOVATION
│  AdaptiveRecalibrationEngine        │    Gemini generates structural patch
└──────────────────┬──────────────────┘    + site instructions
                   │
                   ▼
          [IMPACT MODEL + REPORT]
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Gemini API Key
```bash
export GEMINI_API_KEY="your_key_here"
```
Or edit `config.py` directly.

### 3. Run the full pipeline
```bash
cd nexus_v5
python nexus_pipeline.py
```

### 4. Start the REST API (demo mode)
```bash
uvicorn api.server:app --reload --port 8000
# Then open: http://localhost:8000/docs
```

---

## File Structure

```
nexus_v5/
├── config.py                    # All constants, thresholds, model names
├── requirements.txt
├── nexus_pipeline.py            # ← MAIN ORCHESTRATOR (run this for demo)
│
├── core/
│   ├── project.py               # ProjectInput dataclass + validation
│   ├── design_module.py         # Layer 1: Generative Design (Gemini + fallback)
│   ├── digital_twin.py          # Layer 2: Monte Carlo simulation
│   ├── sensor_engine.py         # Layer 3: IoT stream + anomaly detection
│   ├── recalibration_engine.py  # Layer 4: ARE — deviation-triggered design fix
│   └── impact_model.py          # Business ROI model
│
├── utils/
│   └── gemini_client.py         # Single Gemini wrapper (swap model here)
│
└── api/
    └── server.py                # FastAPI REST layer for live demo
```

---

## Key Differentiator vs. Existing Tools

| Feature | Autodesk / Revit | Traditional BIM | **NEXUS v5** |
|---|---|---|---|
| Generative design | ✅ | ❌ | ✅ + Indian IS codes |
| Monte Carlo simulation | ❌ | ❌ | ✅ |
| Live IoT sensor integration | ❌ | ❌ | ✅ |
| **Auto-recalibration on deviation** | ❌ | ❌ | **✅ (unique globally)** |
| Trained on Indian standards | ❌ | ❌ | ✅ |
| Works offline (deterministic fallback) | N/A | N/A | ✅ |

---

## Gemini Integration Points

| Module | Model Used | Purpose |
|---|---|---|
| `design_module.py` | `gemini-1.5-pro` | Generate IS-code structural variants |
| `design_module.py` | `gemini-1.5-flash` | Engineer recommendation narrative |
| `digital_twin.py` | `gemini-1.5-flash` | Risk probability narrative |
| `recalibration_engine.py` | `gemini-1.5-flash` | Structural rationale + site instructions |

All Gemini calls route through `utils/gemini_client.py` — change the model in `config.py` once, it propagates everywhere.

---

*NEXUS | L&T CreaTech '26 | Built to Win*
