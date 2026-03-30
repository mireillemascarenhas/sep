app = "Sepsora"
# dashboard.py — Sepsora ICU Command Center
# Run with: streamlit run dashboard.py

import streamlit as st
import requests
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(
    page_title="Sepsora — ICU Command Center",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; }
div[data-testid="stDecoration"] { display: none; }

.page-title { font-size: 26px; font-weight: 600; color: var(--text-primary); letter-spacing: -0.3px; }
.page-sub   { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

:root {
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-muted: #64748b;
    --text-faint: #94a3b8;
    --bg-card: #ffffff;
    --bg-surface: #f8fafc;
    --border: #e2e8f0;
    --red: #dc2626; --red-soft: #fef2f2; --red-border: #fecaca;
    --amber: #d97706; --amber-soft: #fffbeb; --amber-border: #fde68a;
    --blue: #2563eb; --blue-soft: #eff6ff; --blue-border: #bfdbfe;
    --green: #16a34a; --green-soft: #f0fdf4; --green-border: #bbf7d0;
    --purple: #7c3aed;
}

@media (prefers-color-scheme: dark) {
    :root {
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --text-faint: #64748b;
        --bg-card: #1e293b;
        --bg-surface: #0f172a;
        --border: #334155;
        --red-soft: #450a0a; --red-border: #991b1b;
        --amber-soft: #451a03; --amber-border: #92400e;
        --blue-soft: #172554; --blue-border: #1e40af;
        --green-soft: #052e16; --green-border: #166534;
    }
}

.banner { border-radius: 10px; padding: 11px 16px; font-size: 13px; font-weight: 500; margin-bottom: 16px; }
.banner-red   { background: var(--red-soft);   border: 1px solid var(--red-border);   color: var(--red); }
.banner-green { background: var(--green-soft); border: 1px solid var(--green-border); color: var(--green); }

.bed-card { background: var(--bg-card); border: 1.5px solid var(--border); border-radius: 14px; padding: 18px 18px 14px; margin-bottom: 4px; }
.bed-card-red    { border-color: var(--red-border)   !important; background: var(--red-soft)   !important; }
.bed-card-amber  { border-color: var(--amber-border) !important; background: var(--amber-soft) !important; }
.bed-card-blue   { border-color: var(--blue-border)  !important; background: var(--blue-soft)  !important; }
.bed-card-green  { border-color: var(--green-border) !important; background: var(--green-soft) !important; }

.bed-id   { font-size: 10px; font-weight: 600; letter-spacing: 1.2px; color: var(--text-muted); margin-bottom: 4px; font-family: 'DM Mono', monospace; }
.bed-name { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.bed-meta { font-size: 11px; color: var(--text-muted); margin-bottom: 12px; }
.bed-condition { font-size: 11px; color: var(--text-muted); margin-top: 8px; font-style: italic; }

.badge { display: inline-flex; align-items: center; padding: 2px 9px; border-radius: 20px; font-size: 10px; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; }
.badge-red   { background: var(--red-soft);   color: var(--red);   border: 1px solid var(--red-border); }
.badge-amber { background: var(--amber-soft); color: var(--amber); border: 1px solid var(--amber-border); }
.badge-blue  { background: var(--blue-soft);  color: var(--blue);  border: 1px solid var(--blue-border); }
.badge-green { background: var(--green-soft); color: var(--green); border: 1px solid var(--green-border); }

.stat-row { display: flex; gap: 8px; margin: 10px 0 6px; }
.stat-pill { flex: 1; text-align: center; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; padding: 8px 4px; }
.stat-val  { font-size: 18px; font-weight: 700; color: var(--text-primary); line-height: 1.1; font-family: 'DM Mono', monospace; }
.stat-lbl  { font-size: 9px; color: var(--text-faint); font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 2px; }

.vital-box       { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 12px; text-align: center; margin-bottom: 8px; }
.vital-box-alert { border-color: var(--red-border) !important; background: var(--red-soft) !important; }
.vital-label { font-size: 10px; color: var(--text-faint); font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 6px; }
.vital-value { font-size: 26px; font-weight: 700; color: var(--text-primary); font-family: 'DM Mono', monospace; line-height: 1; }
.vital-value-alert { color: var(--red) !important; }
.vital-unit  { font-size: 10px; color: var(--text-faint); margin-top: 3px; }

.sofa-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.sofa-lbl   { width: 100px; font-size: 12px; color: var(--text-secondary); }
.sofa-track { flex: 1; background: var(--border); border-radius: 4px; height: 7px; }
.sofa-fill  { height: 7px; border-radius: 4px; }
.sofa-num   { font-size: 12px; font-weight: 700; color: var(--text-primary); width: 16px; font-family: 'DM Mono', monospace; }

.organ-row  { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
.organ-chip { padding: 4px 11px; border-radius: 6px; font-size: 11px; font-weight: 600; font-family: 'DM Mono', monospace; }
.organ-bad  { background: var(--red-soft);   color: var(--red);   border: 1px solid var(--red-border); }
.organ-good { background: var(--green-soft); color: var(--green); border: 1px solid var(--green-border); }

.rec-box     { background: var(--bg-surface); border-left: 3px solid var(--purple); border-radius: 0 10px 10px 0; padding: 14px 18px; font-size: 13px; color: var(--text-secondary); line-height: 1.8; }
.rec-box-red { border-left-color: var(--red) !important; background: var(--red-soft) !important; }

.lab-row  { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 5px; }
.lab-name { font-size: 13px; color: var(--text-muted); }
.lab-val  { font-size: 15px; font-weight: 700; color: var(--text-primary); font-family: 'DM Mono', monospace; }
.lab-unit { font-size: 11px; color: var(--text-faint); margin-left: 4px; }

.metric-box { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; }
.metric-val { font-size: 22px; font-weight: 700; color: var(--text-primary); font-family: 'DM Mono', monospace; }
.metric-lbl { font-size: 11px; color: var(--text-faint); margin-top: 2px; }

.section-head { font-size: 11px; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; color: var(--text-muted); margin: 20px 0 10px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }

div[data-testid="stButton"] > button { border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; font-size: 13px !important; }
hr { border-color: var(--border) !important; margin: 16px 0 !important; }
.ts { font-size: 11px; color: var(--text-faint); font-family: 'DM Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ── constants ─────────────────────────────────────────────────────────────────
ORGANS   = ["respiratory","coagulation","liver","cardiovascular","cns","renal"]
BED_IDS  = ["BED-1","BED-2","BED-3","BED-4","BED-5"]
HIST_LEN = 40

SEV_BADGE = {"CRITICAL":"badge-red","HIGH":"badge-amber","MODERATE":"badge-blue","LOW":"badge-green"}
SEV_CARD  = {"CRITICAL":"bed-card-red","HIGH":"bed-card-amber","MODERATE":"bed-card-blue","LOW":"bed-card-green"}

def rc(s):
    if s >= 75: return "#dc2626"
    if s >= 50: return "#d97706"
    if s >= 30: return "#2563eb"
    return "#16a34a"

def sofa_color(v):
    if v >= 3: return "#dc2626"
    if v >= 2: return "#d97706"
    if v >= 1: return "#2563eb"
    return "#16a34a"

def vital_state(key, val):
    bounds = {"heart_rate":(60,100),"spo2":(95,100),"respiratory_rate":(12,20),"map_mmhg":(70,110),"temperature":(36.1,37.9)}
    if key not in bounds: return "ok"
    lo, hi = bounds[key]
    return "alert" if (val < lo or val > hi) else "ok"

def fetch_all():
    try: return requests.get(f"{API}/patients", timeout=3).json().get("patients", [])
    except: return None

def fetch_one(bid):
    try: return requests.get(f"{API}/patients/{bid}", timeout=3).json()
    except: return None

# ── session state ─────────────────────────────────────────────────────────────
if "view" not in st.session_state:       st.session_state.view = "home"
if "active_bed" not in st.session_state: st.session_state.active_bed = None
if "hist" not in st.session_state:
    st.session_state.hist = {b: {"risk":[],"hr":[],"spo2":[],"map":[],"rr":[],"temp":[],"sbp":[],"dbp":[]} for b in BED_IDS}

def go_home():    st.session_state.view = "home";   st.session_state.active_bed = None
def go_bed(bid):  st.session_state.view = "detail"; st.session_state.active_bed = bid

def push(bid, pt):
    h = st.session_state.hist[bid]; v = pt.get("vitals", {})
    def ap(k, val):
        h[k].append(val)
        if len(h[k]) > HIST_LEN: h[k].pop(0)
    ap("risk", pt.get("risk_score", 0))
    ap("hr",   v.get("heart_rate", 0))
    ap("spo2", v.get("spo2", 0))
    ap("map",  v.get("map_mmhg", 0))
    ap("rr",   v.get("respiratory_rate", 0))
    ap("temp", v.get("temperature", 0))
    ap("sbp",  v.get("systolic_bp", 0))
    ap("dbp",  v.get("diastolic_bp", 0))

def sparkline(vals, color, height=55):
    if len(vals) < 2: return None
    r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=vals, mode="lines",
        line=dict(color=color, width=1.8, shape="spline", smoothing=1.1),
        fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.08)", showlegend=False))
    fig.update_layout(height=height, margin=dict(t=0,b=0,l=0,r=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False,fixedrange=True), yaxis=dict(visible=False,fixedrange=True))
    return fig

def vital_graphs(bid):
    specs = [
        ("hr",  "Heart Rate","#e11d48","bpm"),
        ("spo2","SpO2",      "#2563eb","%"),
        ("map", "MAP",       "#7c3aed","mmHg"),
        ("rr",  "Resp Rate", "#059669","/min"),
        ("temp","Temp",      "#d97706","°C"),
        ("sbp", "Systolic",  "#db2777","mmHg"),
    ]
    fig = make_subplots(rows=2, cols=3,
        subplot_titles=[s[1] for s in specs],
        vertical_spacing=0.2, horizontal_spacing=0.08)
    h = st.session_state.hist[bid]
    for i,(key,label,color,unit) in enumerate(specs):
        row,col = (i//3)+1, (i%3)+1
        vals = h.get(key, [])
        if len(vals) < 2: vals = [0,0]
        r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        fig.add_trace(go.Scatter(y=vals, mode="lines", name=label,
            line=dict(color=color, width=2, shape="spline", smoothing=1.1),
            fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.07)", showlegend=False),
            row=row, col=col)
    fig.update_layout(height=320, margin=dict(t=28,b=8,l=8,r=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)",
        tickfont=dict(size=9), fixedrange=True)
    fig.update_annotations(font_size=11)
    return fig

def gauge(risk):
    color = rc(risk)
    fig = go.Figure(go.Indicator(mode="gauge+number", value=risk,
        number={"suffix":"%","font":{"size":28,"color":color},"valueformat":".0f"},
        title={"text":"Sepsis Risk","font":{"size":11,"color":"#94a3b8"}},
        gauge={"axis":{"range":[0,100],"tickwidth":0,"tickvals":[0,25,50,75,100],"tickfont":{"size":9,"color":"#94a3b8"}},
               "bar":{"color":color,"thickness":0.22}, "bgcolor":"rgba(0,0,0,0)", "borderwidth":0,
               "steps":[{"range":[0,30],"color":"rgba(22,163,74,0.08)"},{"range":[30,50],"color":"rgba(37,99,235,0.08)"},
                        {"range":[50,75],"color":"rgba(217,119,6,0.08)"},{"range":[75,100],"color":"rgba(220,38,38,0.08)"}],
               "threshold":{"line":{"color":"#dc2626","width":2},"thickness":0.85,"value":75}}))
    fig.update_layout(height=195, margin=dict(t=20,b=0,l=10,r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

# ═════════════════════════════════════════════════════════════════════════════
#  DETAIL VIEW
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.view == "detail" and st.session_state.active_bed:
    bid = st.session_state.active_bed
    pt  = fetch_one(bid)

    if not pt or "error" in pt:
        st.error("Could not load patient. Make sure uvicorn is running.")
        if st.button("← Back"): go_home(); st.rerun()
        st.stop()

    push(bid, pt)
    v    = pt.get("vitals", {})
    sofa = pt.get("sofa", {})
    sev  = pt.get("severity", "LOW")

    # back button
    if st.button("← Command Center"):
        go_home(); st.rerun()

    # ── patient switcher ──────────────────────────────────────────────────────
    all_pts = fetch_all() or []
    pt_map  = {p["bed_id"]: p for p in all_pts}

    st.markdown('<div class="section-head">Switch patient</div>', unsafe_allow_html=True)
    sw = st.columns(5)
    for i, b in enumerate(BED_IDS):
        info = pt_map.get(b, {})
        fname = info.get("name", b).split()[0]
        s = info.get("severity", "LOW")
        is_active = (b == bid)
        with sw[i]:
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                f"→ {fname}" if is_active else fname,
                key=f"sw_{b}", use_container_width=True, type=btn_type
            ):
                go_bed(b); st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── patient header ────────────────────────────────────────────────────────
    hc1, hc2 = st.columns([3, 1])
    with hc1:
        bc = SEV_BADGE.get(sev, "badge-green")
        st.markdown(
            f'<div style="margin-bottom:4px">'
            f'<span class="page-title">{pt.get("name","—")}</span>'
            f'&nbsp;&nbsp;<span class="badge {bc}">{sev}</span></div>'
            f'<div class="page-sub">{bid} &nbsp;·&nbsp; Age {pt.get("age","?")} '
            f'&nbsp;·&nbsp; {pt.get("gender","?")} &nbsp;·&nbsp; Admitted {pt.get("admitted","?")} '
            f'&nbsp;·&nbsp; {pt.get("doctor","?")} &nbsp;·&nbsp; {pt.get("ward","?")}</div>'
            f'<div style="font-size:13px;color:var(--text-muted);margin-top:6px">{pt.get("condition","—")}</div>',
            unsafe_allow_html=True)
    with hc2:
        st.plotly_chart(gauge(pt.get("risk_score",0)), use_container_width=True,
                        key="det_gauge", config={"displayModeBar":False})

    # alert banner
    if pt.get("sepsis_alert"):
        st.markdown(f'<div class="banner banner-red">⚠ SEPSIS ALERT &nbsp;·&nbsp; SOFA: {sofa.get("total",0)} &nbsp;·&nbsp; Risk: {pt.get("risk_score",0):.0f}/100 &nbsp;·&nbsp; {len(pt.get("organ_flags",[]))} organ(s) compromised</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="banner banner-green">Within monitored parameters &nbsp;·&nbsp; SOFA: {sofa.get("total",0)} &nbsp;·&nbsp; Risk: {pt.get("risk_score",0):.0f}/100</div>', unsafe_allow_html=True)

    # ── live vitals grid ──────────────────────────────────────────────────────
    st.markdown('<div class="section-head">Live vitals</div>', unsafe_allow_html=True)
    vitals_list = [
        ("heart_rate",       "Heart Rate",   v.get("heart_rate",0),       "bpm"),
        ("spo2",             "SpO2",         v.get("spo2",0),              "%"),
        ("map_mmhg",         "MAP",          v.get("map_mmhg",0),          "mmHg"),
        ("respiratory_rate", "Resp Rate",    v.get("respiratory_rate",0),  "/min"),
        ("temperature",      "Temperature",  v.get("temperature",0),       "°C"),
        ("systolic_bp",      "Systolic BP",  v.get("systolic_bp",0),       "mmHg"),
        ("diastolic_bp",     "Diastolic BP", v.get("diastolic_bp",0),      "mmHg"),
        ("gcs",              "GCS",          v.get("gcs",0),               "/15"),
    ]
    vc = st.columns(4)
    for i,(key,label,val,unit) in enumerate(vitals_list):
        state   = vital_state(key, val)
        box_cls = "vital-box-alert" if state=="alert" else ""
        val_cls = "vital-value-alert" if state=="alert" else ""
        with vc[i%4]:
            st.markdown(
                f'<div class="vital-box {box_cls}">'
                f'<div class="vital-label">{label}</div>'
                f'<div class="vital-value {val_cls}">{val:.1f}</div>'
                f'<div class="vital-unit">{unit}</div></div>',
                unsafe_allow_html=True)

    # ── live vitals graphs ────────────────────────────────────────────────────
    st.markdown('<div class="section-head">Vitals trend</div>', unsafe_allow_html=True)
    st.plotly_chart(vital_graphs(bid), use_container_width=True,
                    key=f"vg_{bid}_{int(time.time())}", config={"displayModeBar":False})

    # ── labs + SOFA side by side ──────────────────────────────────────────────
    lc, sc = st.columns(2)
    with lc:
        st.markdown('<div class="section-head">Lab values</div>', unsafe_allow_html=True)
        for name,val,unit in [
            ("PaO2/FiO2", v.get("pao2_fio2",0), "mmHg"),
            ("Platelets",  v.get("platelets",0),  "×10³/μL"),
            ("Bilirubin",  v.get("bilirubin",0),  "mg/dL"),
            ("Creatinine", v.get("creatinine",0), "mg/dL"),
        ]:
            st.markdown(
                f'<div class="lab-row"><span class="lab-name">{name}</span>'
                f'<span><span class="lab-val">{val:.2f}</span>'
                f'<span class="lab-unit">{unit}</span></span></div>',
                unsafe_allow_html=True)

    with sc:
        st.markdown(f'<div class="section-head">SOFA — {sofa.get("total",0)}/24</div>', unsafe_allow_html=True)
        for organ in ORGANS:
            val   = sofa.get("subscores",{}).get(organ,0)
            color = sofa_color(val)
            st.markdown(
                f'<div class="sofa-row">'
                f'<span class="sofa-lbl">{organ.title()[:11]}</span>'
                f'<div class="sofa-track"><div class="sofa-fill" style="width:{int((val/4)*100)}%;background:{color}"></div></div>'
                f'<span class="sofa-num">{val}</span></div>',
                unsafe_allow_html=True)

    # ── organ flags ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">Organ system status</div>', unsafe_allow_html=True)
    flags = pt.get("organ_flags",[])
    chips = "".join(
        f'<span class="organ-chip {"organ-bad" if o in flags else "organ-good"}">{"⚠ " if o in flags else "✓ "}{o.upper()[:4]}</span>'
        for o in ORGANS)
    st.markdown(f'<div class="organ-row">{chips}</div>', unsafe_allow_html=True)

    # ── recommendation ────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">Clinical recommendation</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="rec-box {"rec-box-red" if sev=="CRITICAL" else ""}">{pt.get("recommendation","—")}</div>',
        unsafe_allow_html=True)

    st.markdown(f'<div style="margin-top:20px" class="ts">Last updated {datetime.now().strftime("%H:%M:%S")} · refreshes every 4s</div>', unsafe_allow_html=True)
    time.sleep(4)
    st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
#  HOME — COMMAND CENTER
# ═════════════════════════════════════════════════════════════════════════════
else:
    h1, h2 = st.columns([5,1])
    with h1:
        st.markdown('<div class="page-title">◈ Sepsora — ICU Command Center</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Sepsis-3 SOFA · Real-time risk scoring · 5 ICU beds</div>', unsafe_allow_html=True)
    with h2:
        live = st.toggle("Live", value=True)

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    patients = fetch_all()
    if patients is None:
        st.error("Cannot reach API. Run: uvicorn main:app --reload")
        st.stop()

    for pt in patients:
        push(pt["bed_id"], pt)

    crits = [p for p in patients if p.get("severity")=="CRITICAL"]
    if crits:
        st.markdown(f'<div class="banner banner-red">⚠ {len(crits)} critical: {", ".join(p["name"] for p in crits)}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="banner banner-green">All beds within monitored parameters</div>', unsafe_allow_html=True)

    # summary metrics
    avg_risk = sum(p.get("risk_score",0) for p in patients) / len(patients)
    mc = st.columns(5)
    for i,(val,lbl) in enumerate([
        ("5", "Beds monitored"),
        (str(len(crits)), "Critical"),
        (str(len([p for p in patients if p.get("severity")=="HIGH"])), "High risk"),
        (f"{avg_risk:.0f}%", "Avg risk"),
        (datetime.now().strftime("%H:%M:%S"), "Updated"),
    ]):
        with mc[i]:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-head">ICU Beds — tap to view patient details</div>', unsafe_allow_html=True)

    # 3 + 2 layout
    for row_pts in [patients[:3], patients[3:]]:
        if not row_pts: continue
        cols = st.columns(len(row_pts))
        for i, pt in enumerate(row_pts):
            bid   = pt["bed_id"]
            risk  = pt.get("risk_score",0)
            sev   = pt.get("severity","LOW")
            v     = pt.get("vitals",{})
            hist  = st.session_state.hist[bid]["risk"]
            cc    = SEV_CARD.get(sev,"")
            bc    = SEV_BADGE.get(sev,"badge-green")

            with cols[i]:
                st.markdown(
                    f'<div class="bed-card {cc}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
                    f'<div><div class="bed-id">{bid}</div>'
                    f'<div class="bed-name">{pt.get("name","—")}</div>'
                    f'<div class="bed-meta">Age {pt.get("age","?")} · {pt.get("gender","?")}</div></div>'
                    f'<span class="badge {bc}">{sev}</span></div>'
                    f'<div class="stat-row">'
                    f'<div class="stat-pill"><div class="stat-val" style="color:{rc(risk)}">{risk:.0f}</div><div class="stat-lbl">Risk %</div></div>'
                    f'<div class="stat-pill"><div class="stat-val">{pt.get("sofa",{}).get("total",0)}</div><div class="stat-lbl">SOFA</div></div>'
                    f'<div class="stat-pill"><div class="stat-val">{v.get("heart_rate",0):.0f}</div><div class="stat-lbl">HR bpm</div></div>'
                    f'<div class="stat-pill"><div class="stat-val">{v.get("spo2",0):.0f}</div><div class="stat-lbl">SpO2 %</div></div>'
                    f'</div>'
                    f'<div class="bed-condition">{pt.get("condition","—")}</div></div>',
                    unsafe_allow_html=True)

                sp = sparkline(hist, rc(risk))
                if sp:
                    st.plotly_chart(sp, use_container_width=True,
                                    key=f"sp_{bid}", config={"displayModeBar":False})

                if st.button(f"View {pt.get('name','').split()[0]} →", key=f"go_{bid}", use_container_width=True):
                    go_bed(bid); st.rerun()

        st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)

    st.markdown(f'<div style="margin-top:16px" class="ts">Sepsora · {datetime.now().strftime("%d %b %Y %H:%M:%S")} · Sepsis-3</div>', unsafe_allow_html=True)

    if live:
        time.sleep(4)
        st.rerun()