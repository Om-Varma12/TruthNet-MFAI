# TruthNet — Fake News Verification System

An end-to-end AI-powered fake news verification pipeline. Takes a news headline, source domain, and social media engagement — then returns a grounded verdict with probability scores and web-search-backed evidence.

---

## Architecture Overview

```
                  Headline + Domain + Tweet Count
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │  1. Semantic Embedding (RoBERTa)            │
        │     sentence-transformers/all-roberta-large-v1
        │     → 1024-dim dense vector                 │
        └──────────────────┬──────────────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  2. Signal Extraction               │
        │  • Source credibility score         │
        │  • Sentiment (HuggingFace pipeline) │
        │  • Clickbait word density           │
        │  • Trigger word density             │
        │  • Writing style score (caps/!)     │
        │  • Named-entity fact signal (spaCy) │
        └──────────┬──────────────────────────┘
                   │  1024-dim embed + 7 handcrafted features
        ┌──────────▼──────────┐
        │  3. XGBoost Classifier │
        │  200 trees, depth 6  │
        │  GPU-accelerated     │
        └──────────┬──────────┘
                   │  binary prediction (REAL/FAKE)
        ┌──────────▼──────────────────────────┐
        │  4. Bayesian Network (pgMPy)         │
        │  Variables: RealNews ← XGBPrediction │
        │           + Credibility, Sentiment,  │
        │             Clickbait, TriggerWords, │
        │             WritingStyle, FactSignal │
        │  → P(REAL | all signals)             │
        └──────────┬──────────────────────────┘
                   │  {label, prob_real, prob_fake, model_signals}
        ┌──────────▼──────────────────────────┐
        │  5. LLM Query Generation (Groq)       │
        │  • llama-3.1-8b-instant             │
        │  • Generates precise fact-check query│
        │  • Calls tavily_search tool          │
        └──────────┬──────────────────────────┘
                   │
        ┌──────────▼──────────────────────────┐
        │  6. Web Search (Tavily)             │
        │  → Top 5 results with snippets       │
        └──────────┬──────────────────────────┘
                   │
        ┌──────────▼──────────────────────────┐
        │  7. Evidence Synthesis (Groq)        │
        │  • Interprets search results         │
        │  • Writes concise reasoning          │
        └─────────────────────────────────────┘
                   │
              Final Verdict
        {REAL/FAKE, probabilities, evidence, reasoning}
```

---

## Project Structure

```
TruthNet-MFAI/
├── main.py                     # Streamlit web UI
├── pipeline/
│   └── run_pipeline.py         # Orchestrates the full pipeline
├── services/
│   ├── ml_inference.py         # XGBoost + Bayesian Network inference
│   ├── features.py             # Feature extraction functions
│   ├── model_store.py          # Loads all saved models (singleton cache)
│   ├── llm_service.py          # Groq LLM + tool-use for query generation
│   └── search_service.py       # Tavily web search client
├── training/
│   ├── main.ipynb              # Full training notebook (all cells)
│   └── saved_models/           # Trained model artifacts
│       ├── sentence_transformer/
│       ├── xgb_model.json
│       ├── bn_model.pkl
│       ├── sentiment_model.pkl
│       ├── metadata.pkl
│       └── spacy_model/
└── requirements.txt
```

---

## Setup Guide

### Prerequisites

- Python 3.10+
- CUDA-capable GPU (recommended, but CPU works)
- Groq API key ([get one here](https://console.groq.com))
- Tavily API key ([get one here](https://app.tavily.com))

### Step 1 — Clone & Create Environment

```bash
git clone https://github.com/Om-Varma12/TruthNet-MFAI.git
cd TruthNet-MFAI

# Create a fresh conda or venv environment
conda create -n truthnet python=3.10 -y
conda activate truthnet
# OR
python -m venv .venv && source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate                            # Windows
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `requirements.txt` includes GPU versions of PyTorch and XGBoost. If running on CPU only, you may need to replace `torch` with the CPU-only build:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cpu
> ```

### Step 3 — Download spaCy Model

The spaCy NER model must be downloaded separately:

```bash
python -m spacy download en_core_web_sm
```

### Step 4 — Configure API Keys

Create a `.env` file in the project root (copy from `.env.example` if one exists, otherwise create fresh):

```bash
# .env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

> **Never commit `.env` to git.** It is already in `.gitignore`.

### Step 5 — Train Models (Optional — skip if using saved models)

The `training/saved_models/` directory already contains trained model artifacts. If you want to retrain:

1. Obtain the FakeNewsNet dataset and place it at `dataset/FakeNewsNet.csv`
2. Open `training/main.ipynb` in Jupyter
3. Run all cells sequentially
4. Saved models will be written to `training/saved_models/`

Training produces:
- `sentence_transformer/` — fine-tuned RoBERTa embedder
- `xgb_model.json` — XGBoost classifier
- `bn_model.pkl` — Bayesian Network structure + CPDs
- `sentiment_model.pkl` — HuggingFace sentiment pipeline
- `spacy_model/` — spaCy NER model
- `metadata.pkl` — domain scores, clickbait words, trigger words

### Step 6 — Run the App

```bash
python main.py
```

Streamlit will start on `http://localhost:8501`.

---

## How to Use the Web UI

1. **Enter a headline** — paste any news headline or claim you want to verify
2. **Enter the source domain** — e.g. `reuters.com`, `apnews.com`, `unknown-site.net`
3. **Enter tweet count** — social media share count (approximate is fine)
4. **Click "Analyze Headline"** — the pipeline runs and returns a verdict
5. **Try example headlines** — click any of the pre-filled pills at the top to demo the system

---

## Output Format

```python
{
    "is_real": bool,          # True if REAL, False if FAKE
    "support": {
        "label":            # "REAL" or "FAKE"
        "prob_real": 0.87,  # Probability the story is real
        "prob_fake": 0.13,  # Probability the story is fake
        "model_signals": {
            "domain":              "reuters.com",
            "credibility_score":    0.95,   # Source reliability
            "tweet_count":         1200,
            "sentiment_score":     -0.23,   # Negative = suspicious
            "clickbait_score":      0,      # Clickbait words found
            "trigger_density":      0.0,    # Trigger word density
            "writing_style_score":  0.01,   # Caps/exclamation ratio
            "fact_signal":          1,      # Has named entities
            "xgb_prediction":       1,       # XGBoost raw output
            "bn_evidence": {...}            # BN inference evidence
        },
        "generated_query":  # LLM-generated search query
        "search_results": [ # Web-grounded evidence
            {
                "title":   str,
                "snippet": str,
                "link":    str
            },
            ...
        ],
        "reason": str       # LLM's explanation of the verdict
    }
}
```

---

## Model Details

### XGBoost Classifier
- 200 estimators, max depth 6, learning rate 0.1
- Feature vector: 1024-dim RoBERTa embedding + 7 handcrafted features
- Trained on FakeNewsNet dataset (balanced via oversampling)
- ~95% accuracy on held-out test set

### Bayesian Network
- Structure learned via domain knowledge (not structure learning):
  ```
  TriggerWords → Clickbait
  Clickbait → Sentiment
  WritingStyle → Credibility
  TweetSignal → Credibility
  FactSignal → Credibility
  Credibility → RealNews
  Sentiment → RealNews
  Clickbait → RealNews
  XGBPrediction → RealNews
  ```
- CPDs estimated via Maximum Likelihood on calibration set
- Inference via Variable Elimination (pgMPy)

### Signal Features
| Feature | How It's Computed |
|---|---|
| **Credibility** | Domain score lookup (0.0–1.0) |
| **TweetSignal** | Binary: tweets > 50 |
| **Sentiment** | HuggingFace `distilbert-base-uncased-finetuned-sst-2-english` |
| **Clickbait** | Count of words: shocking, you won't believe, breaking, secret, exposed, what happened next |
| **TriggerWords** | Density of: urgent, alert, massive, scam, exclusive, must see |
| **WritingStyle** | (exclamation marks + ALL-CAPS words) / total words |
| **FactSignal** | spaCy NER: detects PERSON, ORG, GPE entities |

---

## API Keys

| Service | Purpose | Get Key |
|---|---|---|
| **Groq** | LLM inference (query generation + reasoning) | console.groq.com |
| **Tavily** | Web search for fact-check evidence | app.tavily.com |

Both are free tiers available. Store them in `.env` — never hardcode them.
