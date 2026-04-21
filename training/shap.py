"""
SHAP (SHapley Additive exPlanations) evaluation script for TruthNet-MFAI.
Computes feature contributions for individual predictions and prints them to terminal.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import shap
from dotenv import load_dotenv
from services.model_store import load_models
from services.features import build_feature_payload

load_dotenv()


# Feature names for the 7 handcrafted features (last 7 dimensions)
FEATURE_NAMES = [
    "credibility_score",
    "tweet_count",
    "sentiment_score",
    "clickbait_score",
    "trigger_density",
    "writing_style_score",
    "fact_signal",
]


def explain_prediction(title: str, domain: str, tweet_count: int):
    """
    Run inference and compute SHAP values for a single prediction.
    """
    print("=" * 70)
    print(f"SHAP Analysis for: '{title[:60]}{'...' if len(title) > 60 else ''}'")
    print(f"Domain: {domain}  |  Tweet Count: {tweet_count}")
    print("=" * 70)

    # Load models
    print("\n[1/3] Loading models...")
    bundle = load_models()
    xgb_model = bundle["xgb_model"]
    print("      Models loaded.")

    # Build features
    print("\n[2/3] Building feature payload...")
    normalized_domain = domain.lower().replace("https://", "").replace("http://", "").replace("www.", "")
    feature_payload = build_feature_payload(
        bundle=bundle,
        title=title,
        domain=normalized_domain,
        tweet_count=tweet_count,
    )
    xgb_features = feature_payload["xgb_features"]
    evidence = feature_payload["evidence"]
    model_signals = feature_payload["model_signals"]

    print(f"      XGB features shape: {xgb_features.shape}")
    print(f"      (1024 embedding dims + 7 handcrafted features)")

    # Print raw feature values
    print("\n      Raw Feature Values:")
    for fname, fval in model_signals.items():
        if fname != "domain":
            print(f"        {fname:<25}: {fval}")

    # Run XGBoost prediction
    xgb_pred = xgb_model.predict(xgb_features)[0]
    xgb_prob = xgb_model.predict_proba(xgb_features)[0]
    print(f"\n      XGBoost Prediction: {'REAL' if xgb_pred == 1 else 'FAKE'}")
    print(f"      XGBoost Probabilities — FAKE: {xgb_prob[0]:.4f} | REAL: {xgb_prob[1]:.4f}")

    # Compute SHAP values using a prediction function wrapper
    # This avoids SHAP's XGBTreeModelLoader which fails to parse the base_score format
    print("\n[3/3] Computing SHAP values...")

    def predict_proba(X):
        """Wrapper that calls the patched booster's predict directly."""
        return xgb_model.predict_proba(X)

    explainer = shap.Explainer(predict_proba, xgb_features, feature_names=FEATURE_NAMES)
    shap_output = explainer(xgb_features)   # Explanation object

    shap_real = shap_output.values[0][:, 1] 
    base_value = shap_output.base_values[0][1]

    # For binary classification: positive = pushes toward REAL, negative = pushes toward FAKE
    shap_fake = -shap_real

    # Split embedding and handcrafted features
    embedding_shap = shap_real[:1024]
    handcrafted_shap = shap_real[1024:]  # last 7 values

    print("\n" + "=" * 70)
    print("SHAP VALUES — Feature Contributions to REAL Prediction")
    print("=" * 70)
    print("  (Positive = pushes toward REAL | Negative = pushes toward FAKE)")
    print()

    # Handcrafted features with names
    print(f"  {'Feature':<28} {'Value':>10} {'SHAP':>10}  Interpretation")
    print(f"  {'-'*68}")

    for i, fname in enumerate(FEATURE_NAMES):
        raw_val = model_signals.get(fname, 0)
        shap_val = handcrafted_shap[i]
        # Interpretation
        if shap_val > 0.05:
            interp = f"→ REAL (+{shap_val:.3f})"
        elif shap_val < -0.05:
            interp = f"→ FAKE ({shap_val:.3f})"
        else:
            interp = f"neutral ({shap_val:.3f})"
        print(f"  {fname:<28} {raw_val:>10.4f} {shap_val:>+10.4f}  {interp}")

    # Embedding contribution
    emb_mean = np.mean(np.abs(embedding_shap))
    emb_max = np.max(np.abs(embedding_shap))
    emb_sum = np.sum(embedding_shap)
    print(f"  {'-'*68}")
    print(f"  {'RoBERTa Embedding (1024d)':<28} {'N/A':>10} {emb_sum:>+10.4f}  mean_abs={emb_mean:.4f}, max_abs={emb_max:.4f}")

    # Overall prediction summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Base value (avg model output): {base_value:.4f}")
    print(f"  Sum of SHAP values:            {np.sum(shap_real):.4f}")
    print(f"  Final model output:            {base_value + np.sum(shap_real):.4f}")
    print(f"  Prediction:                     {'REAL' if xgb_pred == 1 else 'FAKE'}")
    print()

    # Top 10 most influential embedding dimensions
    print("=" * 70)
    print("Top 10 Most Influential Embedding Dimensions")
    print("=" * 70)
    top_indices = np.argsort(np.abs(embedding_shap))[-10:][::-1]
    print(f"  {'Dim Index':>12} {'SHAP Value':>12}  Direction")
    print(f"  {'-'*40}")
    for dim_idx in top_indices:
        direction = "→ REAL" if embedding_shap[dim_idx] > 0 else "→ FAKE"
        print(f"  {dim_idx:>12} {embedding_shap[dim_idx]:>+12.4f}  {direction}")

    print()
    print("=" * 70)
    return {
        "handcrafted_shap": dict(zip(FEATURE_NAMES, handcrafted_shap)),
        "embedding_shap_sum": emb_sum,
        "prediction": "REAL" if xgb_pred == 1 else "FAKE",
    }


def run_batch(csv_path: str, n_samples: int = 5):
    """
    Run SHAP analysis on n random samples from a dataset.
    """
    import pandas as pd

    print(f"\nLoading {n_samples} random samples from dataset...")
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["title", "source_domain", "real"])
    df = df.sample(n=min(n_samples, len(df)), random_state=42)

    for i, (_, row) in enumerate(df.iterrows()):
        print(f"\n{'#'*70}")
        print(f"# SAMPLE {i+1}/{n_samples}")
        print(f"{'#'*70}")
        explain_prediction(
            title=str(row["title"]),
            domain=str(row["source_domain"]),
            tweet_count=int(row["tweet_num"]) if pd.notna(row["tweet_num"]) else 0,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SHAP analysis for TruthNet-MFAI")
    parser.add_argument("--title", type=str, default=None, help="Headline to analyze")
    parser.add_argument("--domain", type=str, default="reuters.com", help="Source domain")
    parser.add_argument("--tweets", type=int, default=100, help="Tweet count")
    parser.add_argument("--dataset", type=str, default=None, help="CSV to sample from")
    parser.add_argument("--n", type=int, default=5, help="Number of samples if using dataset")
    args = parser.parse_args()

    if args.dataset:
        run_batch(args.dataset, n_samples=args.n)
    elif args.title:
        explain_prediction(args.title, args.domain, args.tweets)
    else:
        # Default demo samples
        print("\nRunning demo with sample headlines...\n")
        samples = [
            ("Scientists confirm that vaccines alter human DNA permanently", "unknown-site.com", 5),
            ("Reuters confirms 5000 deaths in major earthquake", "reuters.com", 1200),
            ("SHOCKING: Secret cure exposed — you won't believe this one weird trick!", "viral-site.net", 3),
            ("Central bank raises interest rates by 25 basis points", "apnews.com", 340),
        ]
        for i, (title, domain, tweets) in enumerate(samples):
            print(f"\n{'#'*70}")
            print(f"# DEMO SAMPLE {i+1}/{len(samples)}")
            print(f"{'#'*70}")
            explain_prediction(title, domain, tweets)
