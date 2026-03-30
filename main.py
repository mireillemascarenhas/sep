# main.py — Sepsora ICU Backend
# Run with: uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random, time, math
from typing import Optional

app = FastAPI(title="Sepsora ICU Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
#  5 ICU Patients — fixed identities, dynamic vitals
# ─────────────────────────────────────────────────────────────

PATIENTS = {
    "BED-1": {
        "name":      "Arjun Mehta",
        "age":       58,
        "gender":    "Male",
        "condition": "Post-operative sepsis risk",
        "admitted":  "25 Mar 2026",
        "doctor":    "Dr. Priya Kapoor",
        "ward":      "ICU-A",
        "profile":   "deteriorating",   # will trigger alert
        "start_time": time.time(),
    },
    "BED-2": {
        "name":      "Sunita Verma",
        "age":       71,
        "gender":    "Female",
        "condition": "Pneumonia-induced SIRS",
        "admitted":  "26 Mar 2026",
        "doctor":    "Dr. Rakesh Nair",
        "ward":      "ICU-A",
        "profile":   "slow_deterioration",
        "start_time": time.time(),
    },
    "BED-3": {
        "name":      "Rahul Sharma",
        "age":       44,
        "gender":    "Male",
        "condition": "Abdominal infection monitoring",
        "admitted":  "27 Mar 2026",
        "doctor":    "Dr. Anjali Singh",
        "ward":      "ICU-B",
        "profile":   "stable",
        "start_time": time.time(),
    },
    "BED-4": {
        "name":      "Deepak Joshi",
        "age":       63,
        "gender":    "Male",
        "condition": "Urinary tract sepsis",
        "admitted":  "26 Mar 2026",
        "doctor":    "Dr. Meera Iyer",
        "ward":      "ICU-B",
        "profile":   "recovering",
        "start_time": time.time(),
    },
    "BED-5": {
        "name":      "Fatima Sheikh",
        "age":       52,
        "gender":    "Female",
        "condition": "Catheter-related bloodstream infection",
        "admitted":  "28 Mar 2026",
        "doctor":    "Dr. Sanjay Rao",
        "ward":      "ICU-C",
        "profile":   "critical",        # always high risk
        "start_time": time.time(),
    },
}

# ─────────────────────────────────────────────────────────────
#  SOFA subscoring (Sepsis-3)
# ─────────────────────────────────────────────────────────────

def sofa_respiratory(pao2_fio2):
    if pao2_fio2 >= 400: return 0
    if pao2_fio2 >= 300: return 1
    if pao2_fio2 >= 200: return 2
    if pao2_fio2 >= 100: return 3
    return 4

def sofa_coagulation(platelets):
    if platelets >= 150: return 0
    if platelets >= 100: return 1
    if platelets >= 50:  return 2
    if platelets >= 20:  return 3
    return 4

def sofa_liver(bilirubin):
    if bilirubin < 1.2:   return 0
    if bilirubin <= 1.9:  return 1
    if bilirubin <= 5.9:  return 2
    if bilirubin <= 11.9: return 3
    return 4

def sofa_cardiovascular(map_mmhg):
    if map_mmhg >= 70: return 0
    if map_mmhg >= 60: return 1
    if map_mmhg >= 50: return 2
    return 3

def sofa_cns(gcs):
    if gcs == 15: return 0
    if gcs >= 13: return 1
    if gcs >= 10: return 2
    if gcs >= 6:  return 3
    return 4

def sofa_renal(creatinine):
    if creatinine < 1.2:   return 0
    if creatinine <= 1.9:  return 1
    if creatinine <= 3.4:  return 2
    if creatinine <= 4.9:  return 3
    return 4

# ─────────────────────────────────────────────────────────────
#  Live vitals generator — realistic fluctuations per profile
# ─────────────────────────────────────────────────────────────

def generate_vitals(bed_id: str) -> dict:
    p       = PATIENTS[bed_id]
    profile = p["profile"]
    t       = time.time() - p["start_time"]   # seconds since admission
    wave    = math.sin(t / 8)                  # natural oscillation

    # Base vitals by profile
    bases = {
        "deteriorating":      {"hr": 98,  "sbp": 105, "dbp": 68, "rr": 21, "spo2": 95, "temp": 38.4, "pao2": 310, "plt": 130, "bili": 1.4, "map": 68, "gcs": 14, "creat": 1.3},
        "slow_deterioration": {"hr": 92,  "sbp": 112, "dbp": 72, "rr": 19, "spo2": 96, "temp": 38.1, "pao2": 340, "plt": 145, "bili": 1.1, "map": 72, "gcs": 15, "creat": 1.1},
        "stable":             {"hr": 78,  "sbp": 122, "dbp": 80, "rr": 16, "spo2": 98, "temp": 37.2, "pao2": 390, "plt": 160, "bili": 0.8, "map": 82, "gcs": 15, "creat": 0.9},
        "recovering":         {"hr": 75,  "sbp": 118, "dbp": 78, "rr": 15, "spo2": 98, "temp": 37.0, "pao2": 395, "plt": 170, "bili": 0.7, "map": 85, "gcs": 15, "creat": 0.8},
        "critical":           {"hr": 118, "sbp": 88,  "dbp": 52, "rr": 26, "spo2": 91, "temp": 39.1, "pao2": 180, "plt": 68,  "bili": 3.2, "map": 54, "gcs": 11, "creat": 2.8},
    }

    # Drift multiplier — deteriorating profiles get slowly worse over time
    drift = {
        "deteriorating":      min(t / 300, 0.35),
        "slow_deterioration": min(t / 600, 0.15),
        "stable":             0.0,
        "recovering":         -min(t / 400, 0.1),  # improving
        "critical":           min(t / 200, 0.5),
    }

    b = bases[profile]
    d = drift[profile]
    n = lambda scale: random.gauss(0, scale)

    hr    = round(b["hr"]   + d * 18 + wave * 3  + n(2),   1)
    sbp   = round(b["sbp"]  - d * 15 + wave * 2  + n(2),   1)
    dbp   = round(b["dbp"]  - d * 8  + wave * 1  + n(1),   1)
    rr    = round(b["rr"]   + d * 6  + wave * 1  + n(0.5), 1)
    spo2  = round(min(100, b["spo2"] - d * 5 + wave * 0.5 + n(0.3)), 1)
    temp  = round(b["temp"] + d * 0.8 + wave * 0.1 + n(0.05), 1)
    map_  = round((sbp + 2 * dbp) / 3, 1)

    # Lab values (change slower)
    pao2  = round(max(60, b["pao2"]  - d * 100 + n(5)),  1)
    plt   = round(max(10, b["plt"]   - d * 60  + n(3)),  1)
    bili  = round(max(0.3, b["bili"] + d * 2.5 + n(0.1)), 2)
    gcs   = max(3, min(15, round(b["gcs"] - d * 4 + n(0.2))))
    creat = round(max(0.4, b["creat"] + d * 1.5 + n(0.05)), 2)

    # SOFA subscores
    subscores = {
        "respiratory":    sofa_respiratory(pao2),
        "coagulation":    sofa_coagulation(plt),
        "liver":          sofa_liver(bili),
        "cardiovascular": sofa_cardiovascular(map_),
        "cns":            sofa_cns(gcs),
        "renal":          sofa_renal(creat),
    }
    sofa_total = sum(subscores.values())

    # Risk score 0-100
    risk_score = round(min(100, (sofa_total / 24) * 100 + d * 25), 1)

    # Sepsis alert if SOFA >= 6 or risk > 60
    sepsis_alert = sofa_total >= 6 or risk_score >= 60

    # Organ flags (subscores >= 2 are flagged)
    organ_flags = [o for o, v in subscores.items() if v >= 2]

    # Clinical recommendation based on severity
    if risk_score >= 75:
        recommendation = "INITIATE SEPSIS-6 BUNDLE IMMEDIATELY: Blood cultures x2, IV broad-spectrum antibiotics, IV fluid resuscitation 30ml/kg, measure lactate, hourly urine output monitoring, oxygen therapy."
        severity = "CRITICAL"
    elif risk_score >= 50:
        recommendation = "ESCALATE CARE: Repeat blood cultures, review antibiotic coverage, increase monitoring frequency to every 30 minutes, alert senior physician, consider ICU upgrade."
        severity = "HIGH"
    elif risk_score >= 30:
        recommendation = "MONITOR CLOSELY: Reassess vitals every hour, check inflammatory markers (CRP, procalcitonin), ensure IV access, review fluid balance."
        severity = "MODERATE"
    else:
        recommendation = "Continue standard monitoring. Reassess in 4 hours. Maintain fluid balance and continue current treatment plan."
        severity = "LOW"

    return {
        "bed_id":         bed_id,
        "timestamp":      time.time(),
        "vitals": {
            "heart_rate":        hr,
            "systolic_bp":       sbp,
            "diastolic_bp":      dbp,
            "map_mmhg":          map_,
            "respiratory_rate":  rr,
            "spo2":              spo2,
            "temperature":       temp,
            "pao2_fio2":         pao2,
            "platelets":         plt,
            "bilirubin":         bili,
            "gcs":               gcs,
            "creatinine":        creat,
        },
        "sofa": {
            "total":      sofa_total,
            "subscores":  subscores,
        },
        "risk_score":      risk_score,
        "severity":        severity,
        "sepsis_alert":    sepsis_alert,
        "organ_flags":     organ_flags,
        "recommendation":  recommendation,
    }

# ─────────────────────────────────────────────────────────────
#  API Endpoints
# ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"app": "Sepsora ICU Intelligence Layer", "status": "online", "beds": len(PATIENTS)}

@app.get("/patients")
def get_all_patients():
    results = []
    for bed_id, info in PATIENTS.items():
        vitals_data = generate_vitals(bed_id)
        results.append({
            **info,
            "bed_id": bed_id,
            **vitals_data,
        })
    return {"patients": results}

@app.get("/patients/{bed_id}")
def get_patient(bed_id: str):
    bed_id = bed_id.upper()
    if bed_id not in PATIENTS:
        return {"error": f"{bed_id} not found"}
    info        = PATIENTS[bed_id]
    vitals_data = generate_vitals(bed_id)
    return {**info, "bed_id": bed_id, **vitals_data}

@app.get("/alerts")
def get_alerts():
    alerts = []
    for bed_id in PATIENTS:
        v = generate_vitals(bed_id)
        if v["sepsis_alert"]:
            alerts.append({
                "bed_id":      bed_id,
                "patient":     PATIENTS[bed_id]["name"],
                "risk_score":  v["risk_score"],
                "severity":    v["severity"],
                "sofa":        v["sofa"]["total"],
                "organ_flags": v["organ_flags"],
            })
    return {"alerts": alerts, "count": len(alerts)}