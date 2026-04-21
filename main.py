import streamlit as st
import threading
import time as _time

from pipeline.run_pipeline import invokePipeline

st.set_page_config(
    page_title="TruthNet · Neural Verifier",
    page_icon="",
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
#  NEURAL INTERFACE — White Theme CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── CSS VARIABLES ── */
:root {
    --bg:            #F7F8FC;
    --surface:       rgba(255,255,255,0.92);
    --surface-hover: rgba(255,255,255,1);
    --glass:         rgba(255,255,255,0.65);
    --border:        rgba(15,23,42,0.08);
    --border-hover:  rgba(15,23,42,0.15);
    --shadow-sm:     0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
    --shadow-md:     0 4px 16px rgba(15,23,42,0.08), 0 2px 6px rgba(15,23,42,0.04);
    --shadow-lg:     0 12px 40px rgba(15,23,42,0.10), 0 4px 16px rgba(15,23,42,0.06);
    --shadow-glow:   0 0 0 1px rgba(99,102,241,0.15), 0 4px 20px rgba(99,102,241,0.08);

    --text-primary:  #0F172A;
    --text-secondary:#475569;
    --text-muted:   #94A3B8;
    --text-faint:   #CBD5E1;

    --accent:        #6366F1;
    --accent-light:  rgba(99,102,241,0.08);
    --accent-glow:   rgba(99,102,241,0.20);

    --green:         #10B981;
    --green-light:   rgba(16,185,129,0.08);
    --green-border:  rgba(16,185,129,0.20);

    --red:           #EF4444;
    --red-light:     rgba(239,68,68,0.08);
    --red-border:    rgba(239,68,68,0.20);

    --cyan:          #06B6D4;
    --cyan-light:    rgba(6,182,212,0.08);

    --grid-color:    rgba(15,23,42,0.04);
}

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--bg) !important;
    background-image:
        radial-gradient(circle at 20% 20%, rgba(99,102,241,0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(6,182,212,0.03) 0%, transparent 50%),
        linear-gradient(rgba(15,23,42,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(15,23,42,0.015) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 60% 40% at 10% 0%, rgba(99,102,241,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 90% 100%, rgba(6,182,212,0.03) 0%, transparent 60%),
        var(--bg) !important;
}

[data-testid="stSidebar"],
#MainMenu, footer, header, .stDeployButton { display: none !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(15,23,42,0.12); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(15,23,42,0.20); }

/* ── TYPOGRAPHY ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}
p, span, div, label, input, textarea {
    font-family: 'DM Sans', sans-serif !important;
}
code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── COLUMN PADDING ── */
[data-testid="column"] { padding: 0 6px !important; }
.stMarkdown { margin: 0 !important; }
[data-testid="stVerticalBlock"] > div { padding: 0 !important; }

/* ── HEADER ── */
.neural-header {
    padding: 48px 24px 40px;
    text-align: center;
    position: relative;
    animation: fadeSlideDown 0.8s cubic-bezier(0.16,1,0.3,1) both;
}
.neural-header::before {
    content: '';
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(15,23,42,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(15,23,42,0.025) 1px, transparent 1px);
    background-size: 32px 32px;
    mask-image: radial-gradient(ellipse 80% 60% at 50% 0%, black 0%, transparent 70%);
    pointer-events: none;
}
.neural-logo-row {
    display: inline-flex; align-items: center; gap: 16px;
    position: relative;
}
.neural-logo-icon {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #06B6D4 100%);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    box-shadow: 0 8px 24px rgba(99,102,241,0.30), 0 2px 8px rgba(99,102,241,0.20);
    flex-shrink: 0;
    animation: floatBadge 3s ease-in-out infinite;
}
@keyframes floatBadge {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-3px); }
}
.neural-brand {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 38px; font-weight: 700; letter-spacing: -1px;
    background: linear-gradient(135deg, #0F172A 0%, #6366F1 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.neural-version {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px; color: var(--accent);
    background: var(--accent-light);
    border: 1px solid var(--accent-glow);
    padding: 3px 8px; border-radius: 20px; margin-left: 4px;
    letter-spacing: 1.5px; vertical-align: middle;
}
.neural-tagline {
    font-size: 14px; color: var(--text-secondary); margin-top: 8px;
    letter-spacing: 0.3px; font-weight: 300;
}

/* ── SECTION LABEL ── */
.neural-section-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px; letter-spacing: 3px; color: var(--text-muted);
    text-transform: uppercase; margin-bottom: 16px;
    display: flex; align-items: center; gap: 12px;
    animation: fadeSlideDown 0.8s cubic-bezier(0.16,1,0.3,1) both;
}
.neural-section-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(15,23,42,0.08), transparent);
}

/* ── INPUT CARD ── */
.neural-input-card {
    background: var(--surface);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-md);
    animation: fadeSlideUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.1s both;
}
.input-label {
    font-size: 11px; font-weight: 500; color: var(--text-secondary);
    letter-spacing: 0.5px; margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase;
}

/* ── STREAMLIT OVERRIDES ── */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.80) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    transition: all 0.25s cubic-bezier(0.16,1,0.3,1) !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(15,23,42,0.25) !important;
    box-shadow: 0 0 0 3px rgba(15,23,42,0.06) !important;
    background: #ffffff !important;
    outline: none !important;
}
[data-testid="stTextArea"] textarea {
    resize: none !important;
    min-height: 120px !important;
}
[data-testid="stTextArea"] label,
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important; font-weight: 500 !important;
    color: var(--text-muted) !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important; margin-bottom: 6px !important;
}

/* ── BUTTONS — clean white-theme buttons ── */
[data-testid="stMain"] [data-testid="stButton"] > button {
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.3px !important;
    padding: 13px 28px !important;
    border: 1.5px solid rgba(15,23,42,0.15) !important;
    background: #ffffff !important;
    color: #0F172A !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04) !important;
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1) !important;
    cursor: pointer !important;
    width: 100% !important;
}
[data-testid="stMain"] [data-testid="stButton"] > button:hover {
    border-color: rgba(15,23,42,0.30) !important;
    background: #ffffff !important;
    box-shadow: 0 4px 12px rgba(15,23,42,0.10), 0 2px 4px rgba(15,23,42,0.06) !important;
    transform: translateY(-1px) !important;
    color: #0F172A !important;
}
[data-testid="stMain"] [data-testid="stButton"] > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 1px 2px rgba(15,23,42,0.06) !important;
}

/* ── EXAMPLE PILLS ── */
.examples-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px; letter-spacing: 2px; color: var(--text-muted);
    text-transform: uppercase; margin-bottom: 10px;
}
.example-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px; padding: 5px 14px;
    font-size: 11px; color: var(--text-secondary);
    cursor: pointer; margin: 3px;
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
    box-shadow: var(--shadow-sm);
}
.example-pill:hover {
    border-color: var(--accent);
    color: var(--accent);
    box-shadow: var(--shadow-glow);
    transform: translateY(-1px);
}

/* ── PIPELINE ── */
.neural-pipeline {
    background: var(--surface);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 24px 28px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-md);
}
.neural-pipeline-header {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px; letter-spacing: 3px; color: var(--accent);
    text-transform: uppercase; margin-bottom: 20px;
    display: flex; align-items: center; gap: 10px;
}
.blink-dot {
    display: inline-block; width: 7px; height: 7px;
    border-radius: 50%; background: var(--accent);
    animation: pulseDot 1.4s ease-in-out infinite;
    box-shadow: 0 0 8px rgba(99,102,241,0.5);
}
@keyframes pulseDot {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(99,102,241,0.5); }
    50% { opacity: 0.4; box-shadow: 0 0 2px rgba(99,102,241,0.2); }
}

.neural-pipeline-track {
    display: flex; flex-direction: column; gap: 0;
    position: relative;
}
.neural-pipeline-track::before {
    content: ''; position: absolute;
    left: 15px; top: 20px; bottom: 20px; width: 1px;
    background: linear-gradient(to bottom, var(--accent), rgba(99,102,241,0.2));
}
.neural-step {
    display: flex; align-items: center; gap: 14px; padding: 10px 0;
}
.neural-step-dot {
    width: 30px; height: 30px; border-radius: 50%;
    background: var(--bg); border: 2px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0; position: relative; z-index: 1;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
}
.neural-step-dot.done {
    border-color: var(--green);
    background: var(--green-light);
    box-shadow: 0 0 12px rgba(16,185,129,0.25);
}
.neural-step-dot.active {
    border-color: var(--accent);
    background: var(--accent-light);
    box-shadow: 0 0 16px rgba(99,102,241,0.30);
    animation: stepPulse 1.2s ease-in-out infinite;
}
@keyframes stepPulse {
    0%, 100% { box-shadow: 0 0 12px rgba(99,102,241,0.30); }
    50% { box-shadow: 0 0 24px rgba(99,102,241,0.50); }
}
.neural-step-dot.pending { opacity: 0.25; }
.neural-step-name {
    font-size: 13px; font-weight: 500; color: var(--text-secondary);
    transition: color 0.2s;
}
.neural-step-name.done { color: var(--text-primary); }
.neural-step-name.active { color: var(--accent); font-weight: 600; }
.neural-step-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 8px; letter-spacing: 1.5px; margin-left: auto;
    font-weight: 400;
}
.neural-step-label.done { color: var(--green); }
.neural-step-label.active { color: var(--accent); }

/* ── VERDICT CARD ── */
.neural-verdict {
    border-radius: 20px; padding: 28px 32px; margin-bottom: 16px;
    position: relative; overflow: hidden;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: var(--shadow-lg);
    animation: fadeSlideUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.2s both;
}
.neural-verdict.real {
    background: linear-gradient(135deg, rgba(16,185,129,0.06), rgba(16,185,129,0.02));
    border: 1px solid var(--green-border);
}
.neural-verdict.fake {
    background: linear-gradient(135deg, rgba(239,68,68,0.06), rgba(239,68,68,0.02));
    border: 1px solid var(--red-border);
}
.neural-verdict::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 180px; height: 180px; border-radius: 50%; opacity: 0.04;
}
.neural-verdict.real::before { background: var(--green); }
.neural-verdict.fake::before { background: var(--red); }

.neural-verdict-inner { display: flex; align-items: center; gap: 24px; }
.neural-verdict-text { flex: 1; }
.neural-verdict-eyebrow {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px; letter-spacing: 3px; margin-bottom: 8px;
    font-weight: 500;
}
.neural-verdict-eyebrow.real { color: var(--green); }
.neural-verdict-eyebrow.fake { color: var(--red); }
.neural-verdict-title {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 42px; font-weight: 700; letter-spacing: -1px;
    line-height: 1; margin-bottom: 8px;
}
.neural-verdict-title.real { color: var(--green); }
.neural-verdict-title.fake { color: var(--red); }
.neural-verdict-sub {
    font-size: 13px; color: var(--text-secondary); margin-top: 4px;
    font-weight: 300; line-height: 1.5;
}

/* ── PROBABILITY RING ── */
.ring-wrap { text-align: center; flex-shrink: 0; }
.ring-pct-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px; letter-spacing: 1px; margin-top: 6px;
}

/* ── TWO COL PANELS ── */
.neural-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px; }
.neural-panel {
    background: var(--surface);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 20px 24px;
    box-shadow: var(--shadow-md);
}
.panel-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px; letter-spacing: 3px; color: var(--text-muted);
    text-transform: uppercase; margin-bottom: 16px;
}

/* prob bars */
.prob-row { margin: 10px 0; }
.prob-row-head {
    display: flex; justify-content: space-between; margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace !important; font-size: 10px;
}
.prob-bar-bg {
    height: 6px; background: rgba(15,23,42,0.06);
    border-radius: 3px; overflow: hidden;
}
.prob-bar-fill {
    height: 100%; border-radius: 3px;
    transition: width 0.8s cubic-bezier(0.16,1,0.3,1);
}
.prob-bar-fill.real { background: linear-gradient(90deg, #10B981, #34D399); }
.prob-bar-fill.fake { background: linear-gradient(90deg, #EF4444, #F87171); }

/* model breakdown rows */
.model-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0;
}
.model-row + .model-row { border-top: 1px solid var(--border); }
.model-key {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px; color: var(--text-muted); letter-spacing: 1px;
}
.model-val {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 22px; font-weight: 700; letter-spacing: -0.5px;
}

/* ── SIGNAL CHIPS ── */
.neural-chips { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 16px; }
.neural-chip {
    background: var(--surface);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 14px; padding: 14px 16px;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
}
.neural-chip:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}
.neural-chip-name {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 8px; letter-spacing: 2px; color: var(--text-muted);
    text-transform: uppercase; margin-bottom: 10px;
}
.neural-chip-bar {
    height: 4px; background: rgba(15,23,42,0.06);
    border-radius: 2px; margin-bottom: 8px; overflow: hidden;
}
.neural-chip-fill { height: 100%; border-radius: 2px; }
.neural-chip-val {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 18px; font-weight: 700; letter-spacing: -0.5px;
}

/* ── EVIDENCE ── */
.neural-evidence { margin-bottom: 16px; }
.ev-card {
    border-radius: 14px; padding: 16px 20px; margin-bottom: 8px;
    background: var(--surface);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
}
.ev-card:hover {
    border-color: var(--accent);
    box-shadow: var(--shadow-glow);
}
.ev-card.web_result {
    background: linear-gradient(135deg, rgba(99,102,241,0.03), rgba(99,102,241,0.01));
    border-color: rgba(99,102,241,0.12);
}
.ev-tag {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 8px; letter-spacing: 2px; padding: 2px 8px;
    border-radius: 4px; display: inline-block; margin-bottom: 8px;
    text-transform: uppercase; font-weight: 500;
}
.ev-tag.web_result { background: var(--accent-light); color: var(--accent); }
.ev-source {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px; color: var(--text-muted); margin-bottom: 6px;
    letter-spacing: 0.5px;
}
.ev-text { font-size: 12px; color: var(--text-secondary); line-height: 1.7; }
.ev-link-btn {
    display: inline-flex; align-items: center; gap: 5px;
    margin-top: 10px; padding: 5px 12px;
    background: rgba(255,255,255,0.70);
    border: 1px solid var(--border);
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px; letter-spacing: 0.5px; color: var(--text-secondary);
    text-decoration: none;
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
}
.ev-link-btn:hover { border-color: var(--accent); color: var(--accent); }

/* ── BN GRAPH ── */
.bn-divider { height: 1px; background: var(--border); margin: 20px 0; }
.bn-caption {
    font-size: 12px; color: var(--text-secondary); margin-bottom: 14px;
    line-height: 1.7; font-family: 'DM Sans', sans-serif !important;
}
.bn-caption code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px; background: rgba(15,23,42,0.05);
    padding: 1px 5px; border-radius: 3px; color: var(--accent);
}

/* ── QUERY BADGE ── */
.neural-query {
    display: flex; align-items: flex-start; gap: 14px;
    background: var(--accent-light);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;
}
.neural-query-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }
.neural-query-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 8px; letter-spacing: 2px; color: var(--accent);
    text-transform: uppercase; margin-bottom: 4px;
}
.neural-query-text {
    font-size: 12px; color: var(--text-secondary);
    font-style: italic; font-family: 'DM Sans', sans-serif !important;
}

/* ── RECENT ── */
.neural-recent-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: 12px; margin-bottom: 6px;
    background: var(--surface);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
}
.neural-recent-item:hover { border-color: var(--border-hover); box-shadow: var(--shadow-md); }
.neural-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.neural-dot.real { background: var(--green); box-shadow: 0 0 8px rgba(16,185,129,0.4); }
.neural-dot.fake { background: var(--red); box-shadow: 0 0 8px rgba(239,68,68,0.4); }
.neural-recent-hl {
    font-size: 12px; color: var(--text-secondary); flex: 1;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.neural-recent-pct {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px; flex-shrink: 0; font-weight: 500;
}
.neural-recent-pct.real { color: var(--green); }
.neural-recent-pct.fake { color: var(--red); }

/* ── DIVIDER ── */
.neural-divider { height: 1px; background: var(--border); margin: 24px 0; }

/* ── SPINNER ── */
[data-testid="stSpinner"] > div {
    border-color: rgba(99,102,241,0.15) !important;
    border-top-color: var(--accent) !important;
}

/* ── ANIMATIONS ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.animate-in {
    animation: fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) both;
}

/* ── RESPONSIVE ── */
@media (max-width: 640px) {
    .neural-chips { grid-template-columns: repeat(2,1fr) !important; }
    .neural-two-col { grid-template-columns: 1fr !important; }
    .neural-header { padding: 32px 16px 28px; }
    .neural-brand { font-size: 28px; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def _clamp(v, lo=0.0, hi=1.0, default=0.5):
    try: return max(lo, min(hi, float(v)))
    except: return default


def ring_svg(pct, color, size=80):
    r = 26; circ = 2 * 3.14159 * r
    filled = circ * pct; gap = circ - filled
    lbl = f"{round(pct*100)}%"
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 80 80">'
        f'<circle cx="40" cy="40" r="{r}" fill="none" stroke="rgba(15,23,42,0.06)" stroke-width="8"/>'
        f'<circle cx="40" cy="40" r="{r}" fill="none" stroke="{color}" stroke-width="8" '
        f'stroke-dasharray="{filled:.1f} {gap:.1f}" stroke-dashoffset="{circ/4:.1f}" '
        f'stroke-linecap="round" transform="rotate(-90 40 40)" '
        f'style="filter: drop-shadow(0 0 6px {color}40)"/>'
        f'<text x="40" y="36" dominant-baseline="central" text-anchor="middle" '
        f'fill="{color}" font-size="14" font-weight="700" font-family="JetBrains Mono,monospace">{lbl}</text>'
        f'<text x="40" y="50" dominant-baseline="central" text-anchor="middle" '
        f'fill="rgba(15,23,42,0.4)" font-size="7" font-family="JetBrains Mono,monospace">CONFIDENCE</text>'
        f'</svg>'
    )


PIPELINE_STEPS = [
    ("◈", "Semantic Embedding"),
    ("◉", "Signal Extraction"),
    ("◆", "XGBoost + Bayesian"),
    ("◐", "LLM Query Generation"),
    ("◑", "Web Search"),
    ("◒", "Evidence Synthesis"),
]


def pipeline_html(current_step, total_steps):
    done = current_step >= total_steps
    html = '<div class="neural-pipeline">'
    html += '<div class="neural-pipeline-header">'
    html += f'<span class="blink-dot"></span>{"Analysis complete" if done else "Running neural analysis…"}'
    html += '</div>'
    html += '<div class="neural-pipeline-track">'
    for i, (icon, name) in enumerate(PIPELINE_STEPS):
        if i < current_step or done:
            dot_cls = "done";   name_cls = "done";   lbl = "✓ active";   lbl_cls = "done"
        elif i == current_step:
            dot_cls = "active"; name_cls = "active"; lbl = "● running"; lbl_cls = "active"
        else:
            dot_cls = "pending"; name_cls = "";       lbl = "";                lbl_cls = ""
        html += (
            f'<div class="neural-step">'
            f'<div class="neural-step-dot {dot_cls}">{icon}</div>'
            f'<span class="neural-step-name {name_cls}">{name}</span>'
            f'<span class="neural-step-label {lbl_cls}">{lbl}</span>'
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
    verdict = backend.get("label", "REAL")
    confidence = backend.get("confidence", 0.5)
    if verdict == "REAL":
        prob_real = confidence
        prob_fake = 1.0 - confidence
    else:
        prob_real = 1.0 - confidence
        prob_fake = confidence

    ms = support.get("model_signals", {})

    sentiment       = _clamp((float(ms.get("sentiment_score", 0)) + 1.0) / 2.0)
    clickbait_raw   = float(ms.get("clickbait_score", 0))
    clickbait       = _clamp(clickbait_raw / max(clickbait_raw, 5.0))
    trigger_raw     = float(ms.get("trigger_density", 0))
    trigger        = _clamp(trigger_raw / max(trigger_raw, 0.02))
    writing_raw    = float(ms.get("writing_style_score", 0))
    writing        = _clamp(writing_raw / max(writing_raw, 0.05))
    fact_signal    = float(ms.get("fact_signal", 0))
    credibility    = _clamp(ms.get("credibility_score", 0.5))
    tweet_count_raw = float(ms.get("tweet_count", tweet_count))
    viral          = _clamp(tweet_count_raw / max(tweet_count_raw, 20000.0))

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

    xgb_pred = ms.get("xgb_prediction", 1)
    bn_prob_real = support.get("prob_real", 0.5)

    return {
        "verdict":       verdict,
        "probability":   prob_real if verdict == "REAL" else prob_fake,
        "prob_real":     prob_real,
        "prob_fake":     prob_fake,
        "confidence":    confidence,
        "signals": {
            "credibility_score":     round(credibility, 2),
            "sentiment_score":       round(sentiment, 2),
            "clickbait_score":       round(clickbait, 2),
            "trigger_density":       round(trigger, 2),
            "writing_style_score":   round(writing, 2),
            "fact_signal":           round(fact_signal, 2),
            "tweet_count":           round(viral, 2),
            "domain":                ms.get("domain", ""),
        },
        "search_query":  support.get("generated_query", ""),
        "evidence":      evidence,
        "model_breakdown": {
            "xgboost": xgb_pred,
            "bayesian": bn_prob_real,
        },
    }


def chip_color(key, val):
    if key == "credibility_score":   return f"hsl({int(val*120)},65%,42%)"
    if key == "clickbait_score":     return f"hsl({int((1-val)*120)},65%,42%)"
    if key == "fact_signal":         return f"hsl({int(val*120)},65%,42%)"
    return "#6366F1"


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="neural-header">
  <div class="neural-logo-row">
    <div class="neural-logo-icon">◈</div>
    <span class="neural-brand">TruthNet</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN CONTENT
# ─────────────────────────────────────────────
_, col, _ = st.columns([1, 4, 1])
with col:

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    # ── SECTION 01: INPUT
    st.markdown('<div class="neural-section-label">01 &middot; News Signal Input</div>', unsafe_allow_html=True)

    ex = st.session_state.get("ex_selected")
    default_h = ex[0] if ex else ""
    default_d = ex[1] if ex else ""
    default_t = ex[2] if ex else 0

    headline = st.text_area(
        "Headline",
        value=default_h,
        placeholder="Paste or type the news headline you want to verify…",
        height=110,
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
        tweet_count = st.number_input(
            "Tweet Count",
            min_value=0, max_value=10_000_000,
            value=default_t,
            step=100,
            key="tweet_input",
        )

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)


    btn_col, reset_col = st.columns([3, 1], gap="small")
    with btn_col:
        analyze_btn = st.button("Analyze Headline", key="analyze_btn")
    with reset_col:
        clear_btn = st.button("Clear", key="clear_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    if clear_btn:
        st.session_state.ex_selected = None
        st.session_state.result = None
        st.rerun()

    # ── RUN PIPELINE
    if analyze_btn and headline.strip():
        st.session_state.result = None
        st.session_state.run_step = 0
        st.session_state.run_done = False
        st.session_state.run_result = None
        st.session_state.run_error = None

        st.markdown('<div class="neural-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="neural-section-label">02 &middot; Neural Analysis Pipeline</div>', unsafe_allow_html=True)
        prog_ph  = st.empty()
        step_ph  = st.empty()

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
        step_dur    = [0.4, 0.3, 0.6, 0.9, 0.7, 0.9]
        elapsed     = 0.0
        step_idx    = 0

        while _t.is_alive():
            _time.sleep(0.06)
            elapsed += 0.06
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

    # ── RECENT CHECKS
    if st.session_state.history:
        st.markdown('<div class="neural-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="neural-section-label">Recent Checks</div>', unsafe_allow_html=True)
        for item in st.session_state.history[-5:][::-1]:
            cls = item["verdict"].lower()
            disp = f'{round(item["probability"]*100)}% real'
            st.markdown(
                f'<div class="neural-recent-item">'
                f'<div class="neural-dot {cls}"></div>'
                f'<span class="neural-recent-hl">{item["headline"]}</span>'
                f'<span class="neural-recent-pct {cls}">{disp}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── RESULTS
    res = st.session_state.result
    if res is not None:
        st.markdown('<div class="neural-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="neural-section-label">03 &middot; Verdict &amp; Evidence</div>', unsafe_allow_html=True)

        verdict   = res["verdict"]
        prob_real = res["prob_real"]
        prob_fake = res["prob_fake"]
        conf      = res["confidence"]
        vclass    = verdict.lower()
        color     = "#10B981" if verdict == "REAL" else "#EF4444"
        emoji     = "✔" if verdict == "REAL" else "✖"
        mb        = res["model_breakdown"]
        sig_lbl   = {
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
            f'<div class="neural-verdict {vclass}">'
            f'<div class="neural-verdict-inner">'
            f'<div class="neural-verdict-text">'
            f'<div class="neural-verdict-eyebrow {vclass}">◎ VERDICT</div>'
            f'<div class="neural-verdict-title {vclass}">{emoji} {verdict}</div>'
            f'<div class="neural-verdict-sub">{verdict_sub}</div>'
            f'</div>'
            f'<div class="ring-wrap">'
            f'{ring_svg(ring_val, color)}'
            f'<div class="ring-pct-label" style="color:{color}">{ring_label}</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Two-col
        st.markdown('<div class="neural-two-col">', unsafe_allow_html=True)

        # Left: probability bars
        st.markdown(
            '<div class="neural-panel" style="margin-bottom:12px">'
            '<div class="panel-label">Probability Analysis</div>'
            f'<div class="prob-row"><div class="prob-row-head"><span style="color:#10B981">REAL</span><span style="color:#94A3B8">{round(prob_real*100,1)}%</span></div>'
            f'<div class="prob-bar-bg"><div class="prob-bar-fill real" style="width:{prob_real*100:.1f}%"></div></div></div>'
            f'<div class="prob-row"><div class="prob-row-head"><span style="color:#EF4444">FAKE</span><span style="color:#94A3B8">{round(prob_fake*100,1)}%</span></div>'
            f'<div class="prob-bar-bg"><div class="prob-bar-fill fake" style="width:{prob_fake*100:.1f}%"></div></div></div>'
            f'<div style="margin-top:16px;font-size:9px;color:#94A3B8;font-family:\'JetBrains Mono\',monospace;letter-spacing:1px">'
            f'NEURAL CONFIDENCE &nbsp;<span style="color:var(--accent);font-size:13px;font-weight:600">{round(conf*100,1)}%</span>'
            f'</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Right: model breakdown
        xgb_val = verdict
        xgb_color = color
        # BN shows P(real) from the model — if verdict is FAKE, this is 100 - fake_confidence
        bn_pct = round(prob_real * 100, 1)
        bn_val = f"{bn_pct}%"
        st.markdown(
            '<div class="neural-panel">'
            '<div class="panel-label">Model Breakdown</div>'
            f'<div class="model-row"><span class="model-key">XGBoost</span><span class="model-val" style="color:{xgb_color}">{xgb_val}</span></div>'
            f'<div class="model-row"><span class="model-key">Bayesian Net</span><span class="model-val" style="color:{color}">{bn_val}</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)

        # Signal chips
        st.markdown('<div class="neural-section-label" style="margin-bottom:12px">Extracted Neural Signals</div>', unsafe_allow_html=True)

        chips_html = '<div class="neural-chips">'
        domain_val = ""
        for k, v in res["signals"].items():
            if k == "domain":
                domain_val = v
                continue
            c = chip_color(k, v)
            chips_html += (
                f'<div class="neural-chip">'
                f'<div class="neural-chip-name">{sig_lbl.get(k, k)}</div>'
                f'<div class="neural-chip-bar"><div class="neural-chip-fill" style="width:{v*100:.0f}%;background:{c}"></div></div>'
                f'<div class="neural-chip-val" style="color:{c}">{v:.2f}</div>'
                f'</div>'
            )
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)

        if domain_val:
            domain_chip = (
                f'<div class="neural-chips" style="grid-template-columns: 1fr !important;">'
                f'<div class="neural-chip">'
                f'<div class="neural-chip-name">Domain</div>'
                f'<div class="neural-chip-val" style="color:#6366F1;font-size:15px">{domain_val}</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(domain_chip, unsafe_allow_html=True)

        # Search query
        sq = res.get("search_query", "")
        if sq:
            st.markdown(
                f'<div class="neural-query">'
                f'<div class="neural-query-icon">⚲</div>'
                f'<div><div class="neural-query-label">LLM-Generated Query</div>'
                f'<div class="neural-query-text">{sq}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Evidence
        st.markdown('<div class="neural-section-label" style="margin-bottom:12px">Web-Grounded Evidence</div>', unsafe_allow_html=True)
        for ev in res["evidence"]:
            tag = "WEB RESULT"
            link_html = ""
            if ev.get("link"):
                link_html = f'<a href="{ev["link"]}" target="_blank" rel="noopener noreferrer" class="ev-link-btn">→ View Source</a>'
            st.markdown(
                f'<div class="ev-card {ev["type"]}">'
                f'<span class="ev-tag {ev["type"]}">{tag}</span>'
                f'<div class="ev-source">{ev["source"]}</div>'
                f'<div class="ev-text">{ev["text"]}</div>'
                f'{link_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

        # Bayesian Network graph
        bn_toggle = st.button("■  View Bayesian Network Structure", key="bn_toggle")
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
            if st.button("▲  Hide Graph", key="bn_hide"):
                st.session_state.show_bn = False
                st.rerun()

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        st.button("↻  Analyze Another", key="reset_btn")

    st.markdown('<div style="height:50px"></div>', unsafe_allow_html=True)
