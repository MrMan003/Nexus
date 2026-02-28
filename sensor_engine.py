# =============================================================
# NEXUS v5 — Layer 3: IoT Sensor Stream Engine
# Simulates real-time sensor feed + anomaly detection
# =============================================================

import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from config import SENSOR_TOTAL_READINGS, SENSOR_DEVIATION_START


@dataclass
class SensorReading:
    index:       int
    sbc_kNm2:    float
    is_anomaly:  bool = False
    timestamp:   str  = ""         # ISO string in production


@dataclass
class SensorStreamResult:
    readings:           list[SensorReading]
    deviation_detected: bool
    deviation_percent:  float
    alert_level:        str        # NONE / WATCH / WARNING / CRITICAL
    trigger_recal:      bool       # True if recalibration should fire

    def summary(self) -> str:
        if not self.deviation_detected:
            return "✅ Sensor stream normal. No deviation detected."
        return (
            f"⚠️  ALERT [{self.alert_level}] — "
            f"Soil SBC deviated {self.deviation_percent:.1f}% from design value.\n"
            f"Recalibration triggered: {self.trigger_recal}"
        )


class SensorEngine:
    """
    Simulates an MQTT-style IoT sensor stream for SBC monitoring.
    In production: replace simulate_stream() with a Kafka consumer
    reading from real strain gauges / soil sensors.
    """

    def simulate_stream(
        self,
        design_sbc:      float = 180.0,
        deviation_start: int   = SENSOR_DEVIATION_START,
        total:           int   = SENSOR_TOTAL_READINGS,
        seed:            int   = None,
    ) -> SensorStreamResult:

        rng = np.random.default_rng(seed)
        readings: list[SensorReading] = []
        deviation_detected = False

        for i in range(1, total + 1):
            is_anomaly = i >= deviation_start
            if is_anomaly:
                sbc = float(rng.normal(design_sbc * 0.78, 10))
                deviation_detected = True
            else:
                sbc = float(rng.normal(design_sbc, 5))

            readings.append(SensorReading(
                index=i,
                sbc_kNm2=round(sbc, 1),
                is_anomaly=is_anomaly,
            ))

        deviation_percent = 0.0
        if deviation_detected:
            recent_avg = np.mean([r.sbc_kNm2 for r in readings[-5:]])
            deviation_percent = (design_sbc - recent_avg) / design_sbc * 100

        deviation_percent = round(float(deviation_percent), 2)

        alert_level = (
            "CRITICAL" if deviation_percent > 20 else
            "WARNING"  if deviation_percent > 10 else
            "WATCH"    if deviation_percent >  5 else
            "NONE"
        )

        return SensorStreamResult(
            readings           = readings,
            deviation_detected = deviation_detected,
            deviation_percent  = deviation_percent,
            alert_level        = alert_level,
            trigger_recal      = deviation_percent > 5.0,
        )

    @staticmethod
    def ingest_real_readings(raw_values: list[float], design_sbc: float) -> SensorStreamResult:
        """
        Production hook: pass in real sensor readings from Kafka/MQTT.
        Returns same SensorStreamResult structure.
        """
        readings = [SensorReading(index=i+1, sbc_kNm2=v) for i, v in enumerate(raw_values)]
        if len(raw_values) < 3:
            return SensorStreamResult(readings, False, 0.0, "NONE", False)

        recent_avg = np.mean(raw_values[-5:])
        deviation_percent = round((design_sbc - recent_avg) / design_sbc * 100, 2)

        alert_level = (
            "CRITICAL" if deviation_percent > 20 else
            "WARNING"  if deviation_percent > 10 else
            "WATCH"    if deviation_percent >  5 else
            "NONE"
        )
        return SensorStreamResult(
            readings=readings,
            deviation_detected=deviation_percent > 0,
            deviation_percent=deviation_percent,
            alert_level=alert_level,
            trigger_recal=deviation_percent > 5.0,
        )
