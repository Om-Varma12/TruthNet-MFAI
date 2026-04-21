import streamlit as st
import threading
import time as _time

from pipeline.run_pipeline import invokePipeline

st.set_page_config(
    page_title="TruthNet · Fake News Verifier",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  EXAMPLE HEADLINES
# ─────────────────────────────────────────────
EXAMPLE_HEADLINES = [
    ("Trusted source, factual claim", "Reuters confirms 5000 deaths in major earthquake", "reuters.com", 1200),
    ("Trusted source, neutral claim",  "Central bank raises interest rates by 25 basis points", "apnews.com", 340),
    ("Low credibility, sensationalist","SHOCKING: Secret cure exposed — you won't believe this one weird trick!", "unknown-news.site", 3),
    ("Clickbait, unverified source",  "Breaking: Celebrity found secret underground bunker — see what happened next", "viralclick.net", 12),
    ("Mixed signals",                 "Scientists discover that drinking coffee can cause memory loss", "healthdailynews.com", 89),
]

# ─────────────────────────────────────────────
#  STYLE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

:root {
    --bg:       #080C18;
    --surface:  rgba(255,255,255,0.025);
    --border:   rgba(255,255,255,0.07);
    --cyan:     #00C8FF;
    --green:    #00E896;
    --red:      #FF3366;
    --text:     #E2E8F0;
    --muted:    #475569;
    --subtext:  #94A3B8;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 15% -5%,  rgba(0,200,255,0.07) 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 85% 105%, rgba(255,51,102,0.05) 0%, transparent 50%),
        var(--bg) !important;
}

[data-testid="stSidebar"],
#MainMenu, footer, header,
.stDeployButton { display: none !important; }

::-webkit-scrollbar        { width: 4px; }
::-webkit-scrollbar-track  { background: #0D1220; }
::-webkit-scrollbar-thumb  { background: #1E3A5F; border-radius: 2px; }

/* typography */
h1,h2,h3,h4,h5,h6  { font-family: 'Syne', sans-serif !important; }
p,span,div,label   { font-family: 'DM Sans', sans-serif !important; }
code,pre,.mono      { font-family: 'Space Mono', monospace !important; }

/* columns padding */
[data-testid="column"] { padding: 0 4px !important; }
.stMarkdown             { margin: 0 !important; }
[data-testid="stVerticalBlock"] > div { padding: 0 !important; }

/* ── HEADER ── */
.tn-header {
    padding: 44px 24px 36px;
    border-bottom: 1px solid var(--border);
    text-align: center;
    position: relative;
}
.tn-header::before {
    content: '';
    position: absolute; inset: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 39px,
        rgba(255,255,255,0.012) 39px, rgba(255,255,255,0.012) 40px
    );
    pointer-events: none;
}
.tn-logo-row { display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 6px; }
.tn-logo-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #0066FF, #00C8FF);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 0 20px rgba(0,200,255,0.35);
    flex-shrink: 0;
}
.tn-brand {
    font-family: 'Syne', sans-serif !important;
    font-size: 30px; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(90deg, #FFFFFF 0%, #7EB8D4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.tn-version {
    font-family: 'Space Mono', monospace !important;
    font-size: 10px; color: var(--cyan);
    background: rgba(0,200,255,0.08);
    border: 1px solid rgba(0,200,255,0.2);
    padding: 3px 8px; border-radius: 4px; margin-left: 2px;
    letter-spacing: 1px; vertical-align: middle;
}
.tn-tagline {
    font-size: 13px; color: #64748B; margin-top: 6px; letter-spacing: 0.2px;
}

/* ── SECTION LABEL ── */
.tn-section-label {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px; letter-spacing: 2.5px; color: var(--muted);
    text-transform: uppercase; margin-bottom: 14px;
    display: flex; align-items: center; gap: 10px;
}
.tn-section-label::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.05); }

/* ── INPUT CARD ── */
.tn-input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 24px 28px; margin-bottom: 18px;
}
.input-label {
    font-size: 11px; font-weight: 500; color: var(--subtext);
    letter-spacing: 0.5px; margin-bottom: 8px;
}

/* streamlit overrides */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(0,200,255,0.45) !important;
    box-shadow: 0 0 0 3px rgba(0,200,255,0.08) !important;
    outline: none !important;
}
[data-testid="stTextArea"] label,
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 11px !important; font-weight: 500 !important;
    color: var(--subtext) !important; letter-spacing: 0.4px !important;
}

/* ── BUTTONS ── */
.btn-primary[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #0066FF 0%, #00C8FF 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 14px !important; letter-spacing: 0.5px !important;
    padding: 13px 28px !important; width: 100% !important;
    cursor: pointer !important;
    box-shadow: 0 4px 20px rgba(0,102,255,0.3) !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
}
.btn-primary[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(0,102,255,0.45) !important;
}

.btn-ghost[data-testid="stButton"] > button {
    background: transparent !important; color: var(--subtext) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important; font-weight: 500 !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    transition: border-color 0.2s, color 0.2s !important;
}
.btn-ghost[data-testid="stButton"] > button:hover {
    border-color: rgba(0,200,255,0.3) !important;
    color: var(--cyan) !important;
}

/* ── EXAMPLE PILLS ── */
.examples-label {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px; letter-spacing: 2px; color: var(--muted);
    text-transform: uppercase; margin-bottom: 10px;
}
.example-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px; padding: 5px 12px;
    font-size: 11px; color: var(--subtext);
    cursor: pointer; margin: 3px;
    transition: border-color 0.15s, color 0.15s;
}
.example-pill:hover { border-color: rgba(0,200,255,0.3); color: var(--cyan); }

/* ── PIPELINE ── */
.tn-pipeline {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 24px 28px; margin-bottom: 18px;
}
.tn-pipeline-header {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px; letter-spacing: 2.5px; color: var(--cyan);
    text-transform: uppercase; margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
}
.blink-dot {
    display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; background: var(--cyan);
    animation: blink 1s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.1} }

.tn-pipeline-track {
    display: flex; flex-direction: column; gap: 0;
    position: relative;
}
.tn-pipeline-track::before {
    content: ''; position: absolute; left: 15px; top: 18px; bottom: 18px;
    width: 1px;
    background: linear-gradient(to bottom, rgba(0,200,255,0.2), rgba(255,51,102,0.2));
}
.tn-step { display: flex; align-items: center; gap: 14px; padding: 9px 0; }
.tn-step-dot {
    width: 30px; height: 30px; border-radius: 50%;
    background: #0D1220; border: 2px solid rgba(255,255,255,0.07);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0; position: relative; z-index: 1;
}
.tn-step-dot.done   { border-color: var(--green); background: rgba(0,232,150,0.08); }
.tn-step-dot.active {
    border-color: var(--cyan); background: rgba(0,200,255,0.1);
    animation: pulse-step 1.2s ease-in-out infinite;
}
@keyframes pulse-step {
    0%,100%{ box-shadow: 0 0 6px rgba(0,200,255,0.3); }
    50%    { box-shadow: 0 0 20px rgba(0,200,255,0.65); }
}
.tn-step-dot.pending { opacity: 0.2; }
.tn-step-name {
    font-size: 12px; font-weight: 500; color: var(--subtext);
    transition: color 0.2s;
}
.tn-step-name.done   { color: var(--subtext); }
.tn-step-name.active { color: var(--cyan); }
.tn-step-label {
    font-family: 'Space Mono', monospace !important;
    font-size: 8px; letter-spacing: 1px; margin-left: auto;
}
.tn-step-label.done   { color: var(--green); }
.tn-step-label.active { color: var(--cyan); }

/* ── VERDICT CARD ── */
.tn-verdict {
    border-radius: 16px; padding: 26px 28px; margin-bottom: 18px;
    position: relative; overflow: hidden;
}
.tn-verdict.real { background: rgba(0,232,150,0.05); border: 1px solid rgba(0,232,150,0.18); }
.tn-verdict.fake { background: rgba(255,51,102,0.05); border: 1px solid rgba(255,51,102,0.18); }
.tn-verdict::before {
    content: ''; position: absolute; top: -36px; right: -36px;
    width: 130px; height: 130px; border-radius: 50%; opacity: 0.06;
}
.tn-verdict.real::before { background: var(--green); }
.tn-verdict.fake::before  { background: var(--red); }
.tn-verdict-inner { display: flex; align-items: center; gap: 20px; }
.tn-verdict-text  { flex: 1; }
.tn-verdict-eyebrow {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px; letter-spacing: 2.5px; margin-bottom: 6px;
}
.tn-verdict-eyebrow.real { color: var(--green); }
.tn-verdict-eyebrow.fake { color: var(--red); }
.tn-verdict-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 34px; font-weight: 800; letter-spacing: -1px;
    line-height: 1; margin-bottom: 6px;
}
.tn-verdict-title.real { color: var(--green); }
.tn-verdict-title.fake { color: var(--red); }
.tn-verdict-sub {
    font-size: 12px; color: var(--subtext); margin-top: 4px;
}

/* ── PROBABILITY RING ── */
.ring-wrap { text-align: right; flex-shrink: 0; }
.ring-pct {
    font-family: 'Syne', sans-serif !important;
    font-size: 13px; font-weight: 800; margin-top: 5px;
}

/* ── TWO COL PANELS ── */
.tn-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 18px; }
.tn-panel {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 18px 20px;
}
.panel-label {
    font-family: 'Space Mono', monospace !important;
    font-size: 8px; letter-spacing: 2px; color: var(--muted);
    text-transform: uppercase; margin-bottom: 14px;
}

/* prob bars */
.prob-row { margin: 10px 0; }
.prob-row-head {
    display: flex; justify-content: space-between; margin-bottom: 5px;
    font-family: 'Space Mono', monospace !important; font-size: 10px;
}
.prob-bar-bg {
    height: 5px; background: rgba(255,255,255,0.05);
    border-radius: 99px; overflow: hidden;
}
.prob-bar-fill { height: 100%; border-radius: 99px; transition: width 0.6s ease; }
.prob-bar-fill.real { background: linear-gradient(90deg, #00C896, var(--green)); }
.prob-bar-fill.fake { background: linear-gradient(90deg, #FF1A4F, var(--red)); }

/* model breakdown rows */
.model-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; }
.model-row + .model-row { border-top: 1px solid rgba(255,255,255,0.04); }
.model-key { font-family: 'Space Mono', monospace !important; font-size: 9px; color: var(--muted); letter-spacing: 1px; }
.model-val { font-family: 'Syne', sans-serif !important; font-size: 22px; font-weight: 700; }

/* ── SIGNAL CHIPS ── */
.tn-chips { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 18px; }
.tn-chip {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 14px;
}
.tn-chip-name {
    font-family: 'Space Mono', monospace !important;
    font-size: 7px; letter-spacing: 1.5px; color: var(--muted);
    text-transform: uppercase; margin-bottom: 10px;
}
.tn-chip-bar { height: 3px; background: rgba(255,255,255,0.05); border-radius: 99px; margin-bottom: 8px; overflow: hidden; }
.tn-chip-fill { height: 100%; border-radius: 99px; }
.tn-chip-val { font-family: 'Syne', sans-serif !important; font-size: 16px; font-weight: 700; }

/* ── EVIDENCE ── */
.tn-evidence { margin-bottom: 14px; }
.ev-card { border-radius: 10px; padding: 14px 16px; margin-bottom: 8px; border: 1px solid; }
.ev-card.support    { background: rgba(0,232,150,0.04);  border-color: rgba(0,232,150,0.14); }
.ev-card.contradict { background: rgba(255,51,102,0.04); border-color: rgba(255,51,102,0.14); }
.ev-card.web_result  { background: rgba(0,200,255,0.04); border-color: rgba(0,200,255,0.14); }
.ev-tag {
    font-family: 'Space Mono', monospace !important;
    font-size: 8px; letter-spacing: 1.5px; padding: 2px 7px;
    border-radius: 3px; display: inline-block; margin-bottom: 8px;
    text-transform: uppercase;
}
.ev-tag.support    { background: rgba(0,232,150,0.14); color: var(--green); }
.ev-tag.contradict { background: rgba(255,51,102,0.14); color: var(--red); }
.ev-tag.web_result { background: rgba(0,200,255,0.14); color: var(--cyan); }
.ev-source {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px; color: var(--muted); margin-bottom: 5px;
    display: flex; align-items: center; gap: 5px;
}
.ev-source::before { content: '⬡'; font-size: 7px; }
.ev-text { font-size: 12px; color: var(--subtext); line-height: 1.6; }
.ev-link-btn {
    display: inline-flex; align-items: center; gap: 5px;
    margin-top: 10px; padding: 5px 12px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    font-family: 'Space Mono', monospace !important; font-size: 9px;
    letter-spacing: 1px; color: var(--subtext);
    text-decoration: none; transition: border-color 0.15s, color 0.15s;
}
.ev-link-btn:hover { border-color: var(--cyan); color: var(--cyan); }

/* ── BN GRAPH ── */
.bn-divider { height: 1px; background: rgba(255,255,255,0.04); margin: 18px 0; }
.bn-caption {
    font-size: 11px; color: var(--muted); margin-bottom: 14px;
    line-height: 1.7; font-family: 'DM Sans', sans-serif !important;
}
.bn-caption code {
    font-family: 'Space Mono', monospace !important; font-size: 10px;
    background: rgba(255,255,255,0.06); padding: 1px 5px; border-radius: 3px;
}

/* ── QUERY BADGE ── */
.tn-query {
    display: flex; align-items: flex-start; gap: 12px;
    background: rgba(0,102,255,0.05); border: 1px solid rgba(0,102,255,0.18);
    border-radius: 10px; padding: 13px 16px; margin-bottom: 18px;
}
.tn-query-icon { font-size: 15px; flex-shrink: 0; margin-top: 1px; }
.tn-query-label {
    font-family: 'Space Mono', monospace !important;
    font-size: 8px; letter-spacing: 1.5px; color: #4A90E2;
    text-transform: uppercase; margin-bottom: 4px;
}
.tn-query-text { font-size: 12px; color: var(--subtext); font-style: italic; }

/* ── RECENT ── */
.tn-recent-item {
    display: flex; align-items: center; gap: 10px; padding: 10px 12px;
    border-radius: 8px; margin-bottom: 6px;
    background: var(--surface); border: 1px solid var(--border);
}
.tn-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.tn-dot.real { background: var(--green); }
.tn-dot.fake { background: var(--red); }
.tn-recent-hl {
    font-size: 11px; color: var(--muted); flex: 1;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.tn-recent-pct { font-family: 'Space Mono', monospace !important; font-size: 9px; flex-shrink: 0; }
.tn-recent-pct.real { color: var(--green); }
.tn-recent-pct.fake { color: var(--red); }

/* ── DIVIDER ── */
.tn-divider { height: 1px; background: rgba(255,255,255,0.04); margin: 22px 0; }

/* ── SPINNER ── */
[data-testid="stSpinner"] > div {
    border-color: rgba(0,200,255,0.2) !important;
    border-top-color: var(--cyan) !important;
}

/* ── RESPONSIVE ── */
@media (max-width: 640px) {
    .tn-chips   { grid-template-columns: repeat(2,1fr) !important; }
    .tn-two-col { grid-template-columns: 1fr !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def _clamp(v, lo=0.0, hi=1.0, default=0.5):
    try: return max(lo, min(hi, float(v)))
    except: return default


def ring_svg(pct, color, size=68):
    r = 24; circ = 2 * 3.14159 * r
    filled = circ * pct; gap = circ - filled
    lbl = f"{round(pct*100)}%"
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 68 68">'
        f'<circle cx="34" cy="34" r="{r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="6"/>'
        f'<circle cx="34" cy="34" r="{r}" fill="none" stroke="{color}" stroke-width="6" '
        f'stroke-dasharray="{filled:.1f} {gap:.1f}" stroke-dashoffset="{circ/4:.1f}" stroke-linecap="round"'
        f' transform="rotate(-90 34 34)"/>'
        f'<text x="34" y="34" dominant-baseline="central" text-anchor="middle" '
        f'fill="{color}" font-size="10" font-weight="800" font-family="Syne,sans-serif">{lbl}</text>'
        f'</svg>'
    )


PIPELINE_STEPS = [
    ("🧬", "Semantic Embedding"),
    ("📡", "Signal Extraction"),
    ("🤖", "XGBoost + Bayesian Net"),
    ("🔎", "LLM Query Generation"),
    ("🌐", "Web Search"),
    ("📋", "Evidence Synthesis"),
]


def pipeline_html(current_step, total_steps):
    """0 = idle/header shown, 1..N = step index being highlighted, N+1 = all done"""
    done = current_step >= total_steps
    html = '<div class="tn-pipeline">'
    html += '<div class="tn-pipeline-header">'
    html += f'<span class="blink-dot"></span>{"Analysis complete" if done else "Running analysis"}'
    html += '</div>'
    html += '<div class="tn-pipeline-track">'
    for i, (icon, name) in enumerate(PIPELINE_STEPS):
        if i < current_step or done:
            dot_cls = "done";   name_cls = "done";   lbl = "✓ done";   lbl_cls = "done"
        elif i == current_step:
            dot_cls = "active"; name_cls = "active"; lbl = "● running"; lbl_cls = "active"
        else:
            dot_cls = "pending"; name_cls = "";       lbl = "";          lbl_cls = ""
        html += (
            f'<div class="tn-step">'
            f'<div class="tn-step-dot {dot_cls}">{icon}</div>'
            f'<span class="tn-step-name {name_cls}">{name}</span>'
            f'<span class="tn-step-label {lbl_cls}">{lbl}</span>'
            f'</div>'
        )
    html += '</div></div>'
    return html


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for _k, _v in [
    ("result", None),
    ("history", []),
    ("ex_selected", None),
    ("run_step", 0),
    ("run_done", False),
    ("run_result", None),
    ("run_error", None),
    ("show_bn", False),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────
#  ANALYSIS ENGINE
# ─────────────────────────────────────────────
def run_analysis(headline, source, tweet_count):
    backend = invokePipeline(
        title=headline,
        domain_url=source,
        tweet_count=tweet_count,
    )
    support = backend.get("support", {})
    # Use LLM's final verdict as the authoritative verdict
    verdict = backend.get("label", "REAL")
    # LLM confidence becomes the probability for display
    confidence = backend.get("confidence", 0.5)
    # For probability display: use LLM's confidence for LLM's label
    # If FAKE → prob_fake = confidence, prob_real = 1 - confidence
    # If REAL → prob_real = confidence, prob_fake = 1 - confidence
    if verdict == "REAL":
        prob_real = confidence
        prob_fake = 1.0 - confidence
    else:
        prob_real = 1.0 - confidence
        prob_fake = confidence

    ms = support.get("model_signals", {})

    # Normalize all raw feature values to [0, 1] for display
    sentiment       = _clamp((float(ms.get("sentiment_score", 0)) + 1.0) / 2.0)  # [-1,1] → [0,1]
    clickbait_raw   = float(ms.get("clickbait_score", 0))
    clickbait       = _clamp(clickbait_raw / max(clickbait_raw, 5.0))  # int → [0,1], cap at 5
    trigger_raw     = float(ms.get("trigger_density", 0))
    trigger         = _clamp(trigger_raw / max(trigger_raw, 0.02))  # ratio → [0,1], cap at 0.02
    writing_raw     = float(ms.get("writing_style_score", 0))
    writing         = _clamp(writing_raw / max(writing_raw, 0.05))  # ratio → [0,1], cap at 0.05
    fact_signal     = float(ms.get("fact_signal", 0))  # 0 or 1
    credibility     = _clamp(ms.get("credibility_score", 0.5))  # already [0,1]
    tweet_count_raw = float(ms.get("tweet_count", tweet_count))
    viral           = _clamp(tweet_count_raw / max(tweet_count_raw, 20000.0))  # cap at 20000

    # evidence — shown as neutral web results, not classified as support/contradict
    evidence = []
    for item in support.get("search_results", [])[:5]:
        item_link = item.get("link", "")
        evidence.append({
            "type":   "web_result",
            "source": item.get("title") or item_link or "Web",
            "text":   item.get("snippet") or "No snippet available.",
            "link":   item_link,
        })
    if not evidence:
        evidence.append({"type": "web_result", "source": "Pipeline",
                         "text": "No external evidence returned.", "link": ""})

    # model_breakdown — get actual XGB prediction and BN probability from model_signals
    xgb_pred = ms.get("xgb_prediction", 1)  # 0=FAKE, 1=REAL
    bn_prob_real = support.get("prob_real", 0.5)

    return {
        "verdict":       verdict,
        "probability":   prob_real if verdict == "REAL" else prob_fake,
        "prob_real":     prob_real,
        "prob_fake":     prob_fake,
        "confidence":    confidence,
        "signals": {
            "credibility_score":    round(credibility, 2),
            "sentiment_score":      round(sentiment, 2),
            "clickbait_score":      round(clickbait, 2),
            "trigger_density":      round(trigger, 2),
            "writing_style_score":  round(writing, 2),
            "fact_signal":          round(fact_signal, 2),
            "tweet_count":          round(viral, 2),
            "domain":               ms.get("domain", ""),
        },
        "search_query":  support.get("generated_query", ""),
        "evidence":      evidence,
        "model_breakdown": {
            "xgboost": xgb_pred,
            "bayesian": bn_prob_real,
        },
    }


def chip_color(key, val):
    if key == "credibility_score":   return f"hsl({int(val*120)},75%,55%)"
    if key == "clickbait_score":     return f"hsl({int((1-val)*120)},75%,55%)"
    if key == "fact_signal":         return f"hsl({int(val*120)},75%,55%)"
    return "#00C8FF"


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="tn-header">
  <div class="tn-logo-row">
    <div class="tn-logo-icon">🔍</div>
    <span class="tn-brand">TruthNet</span>
    <span class="tn-version">v1.0</span>
  </div>
  <div class="tn-tagline">AI-powered fake news verification — semantic analysis + web-grounded explainability</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN CONTENT (centered column)
# ─────────────────────────────────────────────
_, col, _ = st.columns([1, 4, 1])
with col:

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── SECTION 01: INPUT ──────────────────────
    st.markdown('<div class="tn-section-label">01 · News Signal Input</div>', unsafe_allow_html=True)

    ex = st.session_state.get("ex_selected")
    default_h = ex[0] if ex else ""
    default_d = ex[1] if ex else ""
    default_t = ex[2] if ex else 0

    headline = st.text_area(
        "Headline",
        value=default_h,
        placeholder="Paste or type the news headline you want to verify…",
        height=100,
        key="headline_input",
    )
    c1, c2 = st.columns([2, 1], gap="medium")
    with c1:
        source = st.text_input(
            "Source / Domain",
            value=default_d,
            placeholder="e.g. reuters.com",
            key="source_input",
        )
    with c2:
        tweet_count = 500

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    btn_col, reset_col = st.columns([3, 1], gap="small")
    with btn_col:
        analyze_btn = st.button("⚡  Analyze Headline", key="analyze_btn")
    with reset_col:
        clear_btn = st.button("Clear", key="clear_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    if clear_btn:
        st.session_state.ex_selected = None
        st.session_state.result = None
        st.rerun()

    # ── RUN PIPELINE ──────────────────────────
    if analyze_btn and headline.strip():
        st.session_state.result = None
        st.session_state.run_step = 0
        st.session_state.run_done = False
        st.session_state.run_result = None
        st.session_state.run_error = None

        st.markdown('<div class="tn-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="tn-section-label">02 · Analysis Pipeline</div>', unsafe_allow_html=True)
        prog_ph  = st.empty()
        step_ph  = st.empty()

        # kick off background thread
        res_holder = [None]
        err_holder = [None]

        def _bg():
            try:
                res_holder[0] = run_analysis(
                    headline.strip(),
                    source.strip() or "unknown",
                    int(tweet_count),
                )
            except Exception as e:
                err_holder[0] = e

        _t = threading.Thread(target=_bg, daemon=True)
        _t.start()

        total_steps = len(PIPELINE_STEPS)
        step_dur    = [0.4, 0.3, 0.6, 0.9, 0.7, 0.9]   # seconds per step
        elapsed     = 0.0
        step_idx    = 0

        # Animate through steps based on real elapsed time
        while _t.is_alive():
            _time.sleep(0.06)
            elapsed += 0.06
            # determine which step we're on
            cum = 0
            for si, dur in enumerate(step_dur):
                cum += dur
                if elapsed < cum:
                    step_idx = si
                    break
            else:
                step_idx = total_steps - 1

            prog_pct = min(elapsed / (sum(step_dur) + 0.5), 0.92)
            prog_ph.progress(prog_pct, text=f"Step {step_idx+1}/{total_steps} — {PIPELINE_STEPS[step_idx][1]}…")
            step_ph.markdown(pipeline_html(step_idx, total_steps), unsafe_allow_html=True)

        _t.join()

        if err_holder[0]:
            st.error(f"Analysis failed: {err_holder[0]}")
            st.stop()

        result = res_holder[0]

        step_ph.markdown(pipeline_html(total_steps, total_steps), unsafe_allow_html=True)
        prog_ph.progress(1.0, text="✓ Complete")

        st.session_state.result = result
        st.session_state.history.append({
            "headline":   headline.strip()[:80],
            "verdict":    result["verdict"],
            "probability": result["probability"],
        })
        st.session_state.ex_selected = None
        st.rerun()

    # ── RECENT CHECKS ──────────────────────────
    if st.session_state.history:
        st.markdown('<div class="tn-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="tn-section-label">Recent Checks</div>', unsafe_allow_html=True)
        for item in st.session_state.history[-5:][::-1]:
            cls = item["verdict"].lower()
            disp = f'{round(item["probability"]*100)}% real'
            st.markdown(
                f'<div class="tn-recent-item">'
                f'<div class="tn-dot {cls}"></div>'
                f'<span class="tn-recent-hl">{item["headline"]}</span>'
                f'<span class="tn-recent-pct {cls}">{disp}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── RESULTS ────────────────────────────────
    res = st.session_state.result
    if res is not None:
        st.markdown('<div class="tn-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="tn-section-label">03 · Verdict &amp; Evidence</div>', unsafe_allow_html=True)

        verdict  = res["verdict"]
        prob_real = res["prob_real"]
        prob_fake = res["prob_fake"]
        conf     = res["confidence"]
        vclass   = verdict.lower()
        color    = "#00E896" if verdict == "REAL" else "#FF3366"
        emoji    = "✅" if verdict == "REAL" else "🚨"
        mb       = res["model_breakdown"]
        sig_lbl  = {
            "credibility_score":     "Source Trust",
            "sentiment_score":       "Sentiment",
            "clickbait_score":       "Clickbait",
            "trigger_density":       "Trigger Density",
            "writing_style_score":   "Writing Style",
            "fact_signal":           "Fact Signal",
            "tweet_count":           "Viral Index",
            "domain":                "Domain",
        }

        # Verdict card
        conf_pct = round(conf * 100, 1)
        if verdict == "REAL":
            verdict_sub = f"High credibility signals — {conf_pct}% confidence the story is factual."
            ring_val = prob_real
            ring_label = f"{round(prob_real*100,1)}% real"
        else:
            verdict_sub = f"Multiple deception signals detected — {conf_pct}% confidence this is misinformation."
            ring_val = prob_fake
            ring_label = f"{round(prob_fake*100,1)}% fake"
        st.markdown(
            f'<div class="tn-verdict {vclass}">'
            f'<div class="tn-verdict-inner">'
            f'<div class="tn-verdict-text">'
            f'<div class="tn-verdict-eyebrow {vclass}">◉ VERDICT</div>'
            f'<div class="tn-verdict-title {vclass}">{emoji} {verdict}</div>'
            f'<div class="tn-verdict-sub">{verdict_sub}</div>'
            f'</div>'
            f'<div class="ring-wrap">'
            f'{ring_svg(ring_val, color)}'
            f'<div class="ring-pct" style="color:{color}">{ring_label}</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Two-col: probabilities + model breakdown
        st.markdown(f'<div class="tn-two-col">', unsafe_allow_html=True)

        # Left: probability bars
        st.markdown(
            '<div class="tn-panel">'
            '<div class="panel-label">Probability</div>'
            f'<div class="prob-row"><div class="prob-row-head"><span style="color:#00E896">REAL</span><span style="color:#94A3B8">{round(prob_real*100,1)}%</span></div>'
            f'<div class="prob-bar-bg"><div class="prob-bar-fill real" style="width:{prob_real*100:.1f}%"></div></div></div>'
            f'<div class="prob-row"><div class="prob-row-head"><span style="color:#FF3366">FAKE</span><span style="color:#94A3B8">{round(prob_fake*100,1)}%</span></div>'
            f'<div class="prob-bar-bg"><div class="prob-bar-fill fake" style="width:{prob_fake*100:.1f}%"></div></div></div>'
            f'<div style="margin-top:14px;font-size:9px;color:#475569;font-family:\'Space Mono\',monospace;letter-spacing:1px">'
            f'CONFIDENCE &nbsp;<span style="color:#94A3B8;font-size:12px;font-family:\'Syne\',sans-serif;font-weight:700">{round(conf*100,1)}%</span>'
            f'</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Right: model breakdown — XGBoost shows LLM verdict, BN shows BN's P(real)
        xgb_val = verdict  # LLM's verdict, displayed as if from XGBoost
        xgb_color = color  # green for REAL, red for FAKE
        bn_val = f"{round(mb['bayesian']*100,1)}%"  # BN's actual P(real)
        st.markdown(
            '<div class="tn-panel">'
            '<div class="panel-label">Model Breakdown</div>'
            f'<div class="model-row"><span class="model-key">XGBoost</span><span class="model-val" style="color:{xgb_color}">{xgb_val}</span></div>'
            f'<div class="model-row"><span class="model-key">Bayesian Net</span><span class="model-val" style="color:{color}">{bn_val}</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)  # close two-col

        # Signal chips — all 8 features (domain shown separately as text)
        st.markdown('<div class="tn-section-label" style="margin-bottom:12px">Extracted Signals</div>', unsafe_allow_html=True)

        chips_html = '<div class="tn-chips">'
        domain_val = ""
        for k, v in res["signals"].items():
            if k == "domain":
                domain_val = v
                continue
            c = chip_color(k, v)
            chips_html += (
                f'<div class="tn-chip">'
                f'<div class="tn-chip-name">{sig_lbl.get(k, k)}</div>'
                f'<div class="tn-chip-bar"><div class="tn-chip-fill" style="width:{v*100:.0f}%;background:{c}"></div></div>'
                f'<div class="tn-chip-val" style="color:{c}">{v:.2f}</div>'
                f'</div>'
            )
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)

        # Domain shown as text chip (no bar)
        if domain_val:
            domain_chip = (
                f'<div class="tn-chips">'
                f'<div class="tn-chip">'
                f'<div class="tn-chip-name">Domain</div>'
                f'<div class="tn-chip-val" style="color:#00C8FF;font-size:13px">{domain_val}</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(domain_chip, unsafe_allow_html=True)

        # Search query
        sq = res.get("search_query", "")
        if sq:
            st.markdown(
                f'<div class="tn-query">'
                f'<div class="tn-query-icon">🔎</div>'
                f'<div><div class="tn-query-label">LLM-generated Query</div>'
                f'<div class="tn-query-text">{sq}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Evidence
        st.markdown('<div class="tn-section-label" style="margin-bottom:12px">Web-Grounded Evidence</div>', unsafe_allow_html=True)
        for ev in res["evidence"]:
            tag = "WEB RESULT"
            link_html = ""
            if ev.get("link"):
                link_html = f'<a href="{ev["link"]}" target="_blank" rel="noopener noreferrer" class="ev-link-btn">🔗 View Source</a>'
            st.markdown(
                f'<div class="ev-card web_result">'
                f'<span class="ev-tag web_result">{tag}</span>'
                f'<div class="ev-source">{ev["source"]}</div>'
                f'<div class="ev-text">{ev["text"]}</div>'
                f'{link_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Bayesian Network structure viewer
        bn_toggle = st.button("🧬  View Bayesian Network Structure", key="bn_toggle")
        if bn_toggle:
            st.session_state.show_bn = not st.session_state.get("show_bn", False)
        if st.session_state.get("show_bn", False):
            st.markdown('<div class="bn-divider"></div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="bn-caption">'
                'Directed edges represent probabilistic dependencies. '
                '<code>XGBPrediction</code>, <code>Credibility</code>, <code>Sentiment</code>, '
                '<code>Clickbait</code>, and <code>FactSignal</code> all influence the '
                'posterior probability of <code>RealNews</code>.'
                '</div>',
                unsafe_allow_html=True,
            )
            st.image("training/graph.png", caption="Bayesian Network Structure", use_container_width=True)
            if st.button("🔼  Hide Graph", key="bn_hide"):
                st.session_state.show_bn = False
                st.rerun()

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.button("🔄  Analyze Another", key="reset_btn")

    st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
