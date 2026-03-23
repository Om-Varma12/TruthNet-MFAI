# TruthNet-MFAI

Simple end-to-end fake-news check pipeline.

## What it does

- Takes `title`, `domain/url`, and `tweet_count`.
- Runs model flow: `RoBERTa embeddings -> XGBoost -> Bayesian Network`.
- Uses Groq to generate a Tavily search query and explain why the verdict is real/fake.
- Returns only two top-level fields:
	- `is_real`
	- `support`

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Open `.env` and set keys:

- `GROQ_API_KEY`
- `TAVILY_API_KEY`

## Run

```bash
python main.py
```

You will be prompted for title, domain/url, and tweet count.

## Output shape

```python
{
	"is_real": bool,
	"support": {
		"label": "REAL" or "FAKE",
		"prob_real": float,
		"prob_fake": float,
		"model_signals": {...},
		"generated_query": str,
		"search_results": [
			{"title": str, "snippet": str, "link": str}
		],
		"reason": str
	}
}
```
