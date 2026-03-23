import streamlit as st
import time

from pipeline.run_pipeline import invokePipeline

st.set_page_config(
    page_title="TruthNet · Fake News Verifier",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #080C18 !important;
    color: #E2E8F0 !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0,200,255,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,51,102,0.05) 0%, transparent 55%),
        #080C18 !important;
}

[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0D1220; }
::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 2px; }

h1, h2, h3, h4, h5, h6 { font-family: 'Syne', sans-serif !important; }
p, span, div, label, input, textarea, select, button { font-family: 'DM Sans', sans-serif !important; }
code, pre, .mono { font-family: 'Space Mono', monospace !important; }

/* ── block container reset ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── HERO HEADER ── */
.tn-header {
    padding: 52px 24px 40px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    position: relative;
    overflow: hidden;
    margin-bottom: 0;
    text-align: center;
}
.tn-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 39px,
        rgba(255,255,255,0.015) 39px, rgba(255,255,255,0.015) 40px
    );
    pointer-events: none;
}
.tn-logo-row {
    display: flex; align-items: center; justify-content: center;
    gap: 16px; margin-bottom: 8px;
}
.tn-logo-icon {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #00C8FF, #0066FF);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 24px rgba(0,200,255,0.3);
    flex-shrink: 0;
}
.tn-brand {
    font-family: 'Syne', sans-serif !important;
    font-size: 32px; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(90deg, #FFFFFF 0%, #7EB8D4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.tn-version {
    font-family: 'Space Mono', monospace !important;
    font-size: 10px; color: #00C8FF;
    background: rgba(0,200,255,0.08); border: 1px solid rgba(0,200,255,0.2);
    padding: 3px 8px; border-radius: 4px; margin-left: 4px;
    vertical-align: middle; letter-spacing: 1px;
}
.tn-tagline {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px; color: #64748B; margin-top: 4px; letter-spacing: 0.3px;
}

/* ── SECTION LABELS ── */
.tn-section-label {
    font-family: 'Space Mono', monospace !important;
    font-size: 10px; letter-spacing: 2px; color: #475569;
    text-transform: uppercase; margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
}
.tn-section-label::after {
    content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.06);
}

/* ── INPUT BLOCK ── */
.tn-input-block {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 28px; margin-bottom: 20px;
}

/* Streamlit input overrides */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(0,200,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,200,255,0.08) !important;
    outline: none !important;
}
[data-testid="stTextArea"] label,
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important; font-weight: 500 !important;
    color: #94A3B8 !important; letter-spacing: 0.4px !important;
}

/* ── BUTTON ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #0066FF 0%, #00C8FF 100%) !important;
    color: #FFFFFF !important; border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    letter-spacing: 0.5px !important; padding: 14px 28px !important;
    width: 100% !important; cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px rgba(0,102,255,0.3) !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.92 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(0,102,255,0.45) !important;
}

/* ── PIPELINE ── */
.pipeline-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 28px; margin-bottom: 20px;
}
.pipeline-running-label {
    font-family: 'Space Mono', monospace !important;
    font-size: 10px; letter-spacing: 2px; color: #00C8FF;
    text-transform: uppercase; margin-bottom: 20px;
}
.blink {
    display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; background: #00C8FF;
    animation: blink 1s ease-in-out infinite;
    margin-right: 6px; vertical-align: middle;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.15} }

.pipeline-track { display: flex; flex-direction: column; gap: 0; position: relative; }
.pipeline-track::before {
    content: ''; position: absolute; left: 17px; top: 20px; bottom: 20px;
    width: 1px;
    background: linear-gradient(to bottom, rgba(0,200,255,0.25), rgba(255,51,102,0.25));
}
.pipeline-step {
    display: flex; align-items: center; gap: 16px;
    padding: 11px 0; position: relative;
}
.step-dot {
    width: 34px; height: 34px; border-radius: 50%; background: #0D1220;
    border: 2px solid rgba(255,255,255,0.08);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0; position: relative; z-index: 1; transition: all 0.3s;
}
.step-dot.active {
    border-color: #00C8FF; background: rgba(0,200,255,0.08);
    animation: pulse-ring 1.2s ease-in-out infinite;
}
@keyframes pulse-ring {
    0%,100%{ box-shadow: 0 0 8px rgba(0,200,255,0.3); }
    50%    { box-shadow: 0 0 22px rgba(0,200,255,0.7); }
}
.step-dot.done   { border-color: #00E896; background: rgba(0,232,150,0.08); }
.step-dot.pending { opacity: 0.25; }
.step-info { flex: 1; }
.step-name { font-family: 'DM Sans', sans-serif !important; font-size: 13px; font-weight: 500; color: #94A3B8; }
.step-name.active-name { color: #00C8FF; }
.step-name.done-name   { color: #CBD5E1; }
.step-status { font-family: 'Space Mono', monospace !important; font-size: 9px; letter-spacing: 1px; flex-shrink: 0; }
.step-status.done-label   { color: #00E896; }
.step-status.active-label { color: #00C8FF; }

/* ── VERDICT CARD ── */
.verdict-card {
    border-radius: 16px; padding: 28px; margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.verdict-real { background: rgba(0,232,150,0.06);  border: 1px solid rgba(0,232,150,0.2); }
.verdict-fake { background: rgba(255,51,102,0.06); border: 1px solid rgba(255,51,102,0.2); }
.verdict-card::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 140px; height: 140px; border-radius: 50%; opacity: 0.07;
}
.verdict-real::before { background: #00E896; }
.verdict-fake::before { background: #FF3366; }
.verdict-inner { display: flex; align-items: center; gap: 24px; }
.verdict-text-block { flex: 1; }
.verdict-label { font-family:'Space Mono',monospace !important; font-size:10px; letter-spacing:2px; margin-bottom:6px; }
.verdict-label.real { color: #00E896; }
.verdict-label.fake { color: #FF3366; }
.verdict-title { font-family:'Syne',sans-serif !important; font-size:38px; font-weight:800; letter-spacing:-1px; line-height:1; margin-bottom:4px; }
.verdict-title.real { color: #00E896; }
.verdict-title.fake { color: #FF3366; }
.verdict-subtitle { font-family:'DM Sans',sans-serif !important; font-size:13px; color:#64748B; margin-top:8px; }

/* ── TWO-COL PANELS ── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.two-col-panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px; padding: 18px;
}

/* ── PROB BARS ── */
.prob-bar-wrap { margin: 12px 0; }
.prob-bar-label {
    display: flex; justify-content: space-between; margin-bottom: 6px;
    font-family: 'Space Mono', monospace !important; font-size: 11px;
}
.prob-bar-bg { height: 6px; background: rgba(255,255,255,0.06); border-radius: 99px; overflow: hidden; }
.prob-bar-fill { height: 100%; border-radius: 99px; }
.prob-bar-fill.real { background: linear-gradient(90deg, #00C896, #00E896); }
.prob-bar-fill.fake { background: linear-gradient(90deg, #FF1A4F, #FF3366); }

/* ── SIGNAL CHIPS ── */
.signal-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 20px; }
.signal-chip {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 14px 12px;
}
.signal-chip-name {
    font-family: 'Space Mono', monospace !important; font-size: 8px;
    letter-spacing: 1.2px; color: #475569; text-transform: uppercase; margin-bottom: 8px;
}
.signal-chip-bar { height: 3px; background: rgba(255,255,255,0.05); border-radius: 99px; margin-bottom: 8px; overflow: hidden; }
.signal-chip-fill { height: 100%; border-radius: 99px; }
.signal-chip-val { font-family: 'Syne', sans-serif !important; font-size: 18px; font-weight: 700; }

/* ── EVIDENCE ── */
.evidence-card { border-radius: 10px; padding: 16px; margin-bottom: 10px; border: 1px solid; }
.evidence-card.support    { background: rgba(0,232,150,0.04);  border-color: rgba(0,232,150,0.15); }
.evidence-card.contradict { background: rgba(255,51,102,0.04); border-color: rgba(255,51,102,0.15); }
.evidence-card-tag {
    font-family: 'Space Mono', monospace !important; font-size: 9px; letter-spacing: 1.5px;
    padding: 3px 8px; border-radius: 4px; display: inline-block;
    margin-bottom: 10px; text-transform: uppercase;
}
.evidence-card.support .evidence-card-tag    { background: rgba(0,232,150,0.15);  color: #00E896; }
.evidence-card.contradict .evidence-card-tag { background: rgba(255,51,102,0.15); color: #FF3366; }
.evidence-card-source {
    font-family: 'Space Mono', monospace !important; font-size: 10px; color: #64748B;
    margin-bottom: 6px; display: flex; align-items: center; gap: 6px;
}
.evidence-card-source::before { content: '⬡'; font-size: 8px; }
.evidence-card-text { font-family: 'DM Sans', sans-serif !important; font-size: 13px; color: #94A3B8; line-height: 1.6; }

/* ── QUERY BADGE ── */
.query-badge {
    display: flex; align-items: flex-start; gap: 12px;
    background: rgba(0,102,255,0.06); border: 1px solid rgba(0,102,255,0.2);
    border-radius: 10px; padding: 14px 16px; margin-bottom: 20px;
}
.query-badge-label {
    font-family: 'Space Mono', monospace !important; font-size: 9px;
    letter-spacing: 1.5px; color: #4A90E2; text-transform: uppercase; margin-bottom: 5px;
}
.query-badge-text { font-family: 'DM Sans', sans-serif !important; font-size: 13px; color: #CBD5E1; font-style: italic; }

/* ── RECENT ── */
.recent-item {
    display: flex; align-items: center; gap: 12px; padding: 11px 14px;
    border-radius: 8px; margin-bottom: 8px;
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
}
.recent-badge { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.recent-badge.real { background: #00E896; }
.recent-badge.fake { background: #FF3366; }
.recent-headline {
    font-family: 'DM Sans', sans-serif !important; font-size: 12px; color: #64748B;
    flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.recent-prob { font-family: 'Space Mono', monospace !important; font-size: 10px; flex-shrink: 0; }
.recent-prob.real { color: #00E896; }
.recent-prob.fake { color: #FF3366; }

/* ── DIVIDER ── */
.tn-divider { height: 1px; background: rgba(255,255,255,0.05); margin: 24px 0; }

/* ── STREAMLIT OVERRIDES ── */
[data-testid="column"] { padding: 0 !important; }
.stMarkdown { margin: 0 !important; }
[data-testid="stVerticalBlock"] > div { padding: 0 !important; }
section[data-testid="stSidebar"] { display: none; }
[data-testid="stSpinner"] > div {
    border-color: rgba(0,200,255,0.2) !important;
    border-top-color: #00C8FF !important;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = []

# ── ANALYSIS ENGINE ──
def _clamp01(value, default=0.0):
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def run_analysis(headline, source, tweet_count):
    backend = invokePipeline(
        title=headline,
        domain_url=source,
        tweet_count=tweet_count,
    )

    support = backend.get("support", {})
    verdict = support.get("label", "REAL")
    prob_real = _clamp01(support.get("prob_real", 0.5), default=0.5)
    model_signals = support.get("model_signals", {})

    sentiment = _clamp01((float(model_signals.get("sentiment_score", 0.0)) + 1.0) / 2.0, default=0.5)
    clickbait_raw = float(model_signals.get("clickbait_score", 0.0))
    clickbait = _clamp01(clickbait_raw / 5.0, default=0.0)
    source_credibility = _clamp01(model_signals.get("credibility_score", 0.5), default=0.5)
    viral_index = _clamp01(float(model_signals.get("tweet_count", tweet_count)) / 20000.0, default=0.0)

    search_results = support.get("search_results", [])
    evidence_type = "support" if verdict == "REAL" else "contradict"
    evidence = []
    for item in search_results[:5]:
        evidence.append(
            {
                "type": evidence_type,
                "source": item.get("title") or item.get("link") or "Web source",
                "text": item.get("snippet") or "No snippet available for this result.",
            }
        )

    reason = support.get("reason", "")
    if reason:
        evidence.append(
            {
                "type": evidence_type,
                "source": "Model reasoning",
                "text": reason,
            }
        )

    if not evidence:
        evidence.append(
            {
                "type": evidence_type,
                "source": "Pipeline",
                "text": "No external evidence results were returned.",
            }
        )

    return {
        "verdict": verdict,
        "probability": prob_real,
        "confidence": round(abs(prob_real - 0.5) * 2.0, 3),
        "signals": {
            "source_credibility": round(source_credibility, 2),
            "sentiment_score": round(sentiment, 2),
            "clickbait_score": round(clickbait, 2),
            "viral_index": round(viral_index, 2),
        },
        "search_query": support.get("generated_query", ""),
        "evidence": evidence,
        "model_breakdown": {
            "xgboost": prob_real,
            "bayesian": prob_real,
        },
    }

PIPELINE_STEPS = [
    ("🧬","Semantic Embedding",     2),
    ("📡","Signal Extraction",      0.5),
    ("🤖","XGBoost + Bayesian",     2),
    ("🔎","LLM Query Generation",   8),
    ("🌐","Web Search",             2),
    ("📋","Evidence Summarisation", 5),
]

def build_pipeline_html(done_up_to):
    html = '<div class="pipeline-wrap">'
    html += '<div class="pipeline-running-label"><span class="blink"></span>Running analysis pipeline</div>'
    html += '<div class="pipeline-track">'
    for i,(icon,name,_) in enumerate(PIPELINE_STEPS):
        if i < done_up_to:
            dot,nc,st_ = "done","done-name",'<span class="step-status done-label">✓ done</span>'
        elif i == done_up_to:
            dot,nc,st_ = "active","active-name",'<span class="step-status active-label">● running</span>'
        else:
            dot,nc,st_ = "pending","",""
        html += f'<div class="pipeline-step"><div class="step-dot {dot}">{icon}</div><div class="step-info"><div class="step-name {nc}">{name}</div></div>{st_}</div>'
    html += "</div></div>"
    return html

def ring_svg(pct, color, size=72):
    r=26; circ=2*3.14159*r; filled=circ*pct; gap=circ-filled
    return f'<svg width="{size}" height="{size}" viewBox="0 0 72 72"><circle cx="36" cy="36" r="{r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="5"/><circle cx="36" cy="36" r="{r}" fill="none" stroke="{color}" stroke-width="5" stroke-dasharray="{filled:.1f} {gap:.1f}" stroke-dashoffset="{circ/4:.1f}" stroke-linecap="round"/></svg>'

def chip_color(key, val):
    if key == "source_credibility": return f"hsl({int(val*120)},80%,55%)"
    if key == "clickbait_score":    return f"hsl({int((1-val)*120)},80%,55%)"
    return "#00C8FF"

# ════════════════════════════════
#  HEADER
# ════════════════════════════════
st.markdown("""
<div class="tn-header">
  <div class="tn-logo-row">
    <div class="tn-logo-icon">🔍</div>
    <span class="tn-brand">TruthNet</span>
    <span class="tn-version">v1.0</span>
  </div>
  <div class="tn-tagline">AI-powered fake news verification · Semantic analysis + web-grounded explainability</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════
#  CENTER via flanking columns
# ════════════════════════════════
_, center, _ = st.columns([1, 4, 1])

with center:
    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── INPUT BLOCK ──
    st.markdown('<div class="tn-section-label">01 · News Signal Input</div>', unsafe_allow_html=True)

    headline = st.text_area("Headline", placeholder="Paste or type the news headline you want to verify…", height=110, key="headline_input")
    c1, c2 = st.columns([2, 1], gap="medium")
    with c1:
        source = st.text_input("Source / Domain", placeholder="e.g. reuters.com", key="source_input")
    with c2:
        tweet_count = st.number_input("Tweet Count", min_value=0, max_value=10_000_000, value=0, step=500, key="tweet_input")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("⚡  Analyze Headline", key="analyze_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── PIPELINE ANIMATION (runs on button click, before rerun) ──
    if analyze_btn:
        if not headline.strip():
            st.warning("Please enter a headline to analyze.")
        else:
            st.session_state.result = None
            st.markdown('<div class="tn-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="tn-section-label">02 · Analysis Pipeline</div>', unsafe_allow_html=True)
            pipeline_ph = st.empty()
            for step_idx in range(len(PIPELINE_STEPS)):
                pipeline_ph.markdown(build_pipeline_html(step_idx), unsafe_allow_html=True)
                time.sleep(PIPELINE_STEPS[step_idx][2])
            with st.spinner("Running backend pipeline..."):
                result = run_analysis(headline.strip(), source.strip() or "unknown", tweet_count)
            pipeline_ph.markdown(build_pipeline_html(len(PIPELINE_STEPS)), unsafe_allow_html=True)
            time.sleep(0.35)
            st.session_state.result = result
            st.session_state.history.append({"headline":headline.strip(),"verdict":result["verdict"],"probability":result["probability"]})
            st.rerun()

    # ── RECENT CHECKS ──
    if st.session_state.history:
        st.markdown('<div class="tn-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="tn-section-label">Recent Checks</div>', unsafe_allow_html=True)
        for item in st.session_state.history[-4:][::-1]:
            cls  = item["verdict"].lower()
            disp = f"{round(item['probability']*100)}% real"
            hl_s = (item["headline"][:70]+"…") if len(item["headline"])>70 else item["headline"]
            st.markdown(f'<div class="recent-item"><div class="recent-badge {cls}"></div><span class="recent-headline">{hl_s}</span><span class="recent-prob {cls}">{disp}</span></div>', unsafe_allow_html=True)

    # ── RESULTS ──
    res = st.session_state.result
    if res is not None:
        verdict   = res["verdict"]
        prob      = res["probability"]
        conf      = res["confidence"]
        vclass    = verdict.lower()
        color     = "#00E896" if verdict=="REAL" else "#FF3366"
        emoji     = "✅" if verdict=="REAL" else "🚨"
        fake_prob = round(1-prob, 3)
        mb        = res["model_breakdown"]

        st.markdown('<div class="tn-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="tn-section-label">03 · Verdict &amp; Evidence</div>', unsafe_allow_html=True)

        # Verdict card
        st.markdown(f"""
<div class="verdict-card verdict-{vclass}">
  <div class="verdict-inner">
    <div class="verdict-text-block">
      <div class="verdict-label {vclass}">◉ VERDICT</div>
      <div class="verdict-title {vclass}">{emoji} {verdict}</div>
      <div class="verdict-subtitle">{"Story appears factual — high credibility signals detected." if verdict=="REAL" else "Likely misinformation — multiple deception signals flagged."}</div>
    </div>
    <div style="text-align:right;flex-shrink:0">
      {ring_svg(prob, color)}
      <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:800;color:{color};margin-top:6px">{round(prob*100,1)}% real</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # Prob bars + model breakdown
        st.markdown(f"""
<div class="two-col">
  <div class="two-col-panel">
    <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:1.5px;color:#475569;text-transform:uppercase;margin-bottom:14px">Probability Breakdown</div>
    <div class="prob-bar-wrap">
      <div class="prob-bar-label"><span style="color:#00E896">REAL</span><span style="color:#94A3B8">{round(prob*100,1)}%</span></div>
      <div class="prob-bar-bg"><div class="prob-bar-fill real" style="width:{prob*100:.1f}%"></div></div>
    </div>
    <div class="prob-bar-wrap">
      <div class="prob-bar-label"><span style="color:#FF3366">FAKE</span><span style="color:#94A3B8">{round(fake_prob*100,1)}%</span></div>
      <div class="prob-bar-bg"><div class="prob-bar-fill fake" style="width:{fake_prob*100:.1f}%"></div></div>
    </div>
    <div style="margin-top:14px;font-family:'Space Mono',monospace;font-size:9px;color:#475569;letter-spacing:1px">
      MODEL CONFIDENCE &nbsp;<span style="color:#94A3B8;font-size:13px;font-family:'Syne',sans-serif;font-weight:700">{round(conf*100,1)}%</span>
    </div>
  </div>
  <div class="two-col-panel" style="display:flex;flex-direction:column;gap:8px">
    <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:1.5px;color:#475569;text-transform:uppercase;margin-bottom:4px">Model Breakdown</div>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:14px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-family:'Space Mono',monospace;font-size:10px;color:#475569">XGBoost</span>
        <span style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:{color}">{round(mb['xgboost']*100,1)}%</span>
      </div>
      <div style="height:1px;background:rgba(255,255,255,0.05)"></div>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-family:'Space Mono',monospace;font-size:10px;color:#475569">Bayesian</span>
        <span style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:{color}">{round(mb['bayesian']*100,1)}%</span>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # Signal chips
        st.markdown('<div class="tn-section-label" style="margin-bottom:14px">Extracted Signals</div>', unsafe_allow_html=True)
        sig_labels = {"source_credibility":"Source Trust","sentiment_score":"Sentiment","clickbait_score":"Clickbait","viral_index":"Viral Index"}
        chips_html = '<div class="signal-grid">'
        for key, val in res["signals"].items():
            c = chip_color(key, val)
            chips_html += f'<div class="signal-chip"><div class="signal-chip-name">{sig_labels.get(key,key)}</div><div class="signal-chip-bar"><div class="signal-chip-fill" style="width:{val*100:.0f}%;background:{c}"></div></div><div class="signal-chip-val" style="color:{c}">{val:.2f}</div></div>'
        chips_html += "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)

        # Search query
        st.markdown(f'<div class="query-badge"><div style="font-size:16px;flex-shrink:0">🔎</div><div><div class="query-badge-label">LLM-generated Search Query</div><div class="query-badge-text">{res["search_query"]}</div></div></div>', unsafe_allow_html=True)

        # Evidence
        st.markdown('<div class="tn-section-label" style="margin-bottom:14px">Web-Grounded Evidence</div>', unsafe_allow_html=True)
        for ev in res["evidence"]:
            tag = "SUPPORTS" if ev["type"]=="support" else "CONTRADICTS"
            st.markdown(f'<div class="evidence-card {ev["type"]}"><span class="evidence-card-tag">{tag}</span><div class="evidence-card-source">{ev["source"]}</div><div class="evidence-card-text">{ev["text"]}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("🔄  New Analysis", key="reset_btn"):
            st.session_state.result = None
            st.rerun()

    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)