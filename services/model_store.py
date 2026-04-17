import pickle
from pathlib import Path

import joblib
import spacy
from pgmpy.inference import VariableElimination
from sentence_transformers import SentenceTransformer
from xgboost import XGBClassifier
import torch
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT_DIR / "training" / "saved_models"  # ← retrained models (no oversampling)


_CACHE = None


def _load_serialized(path):
    original_torch_load = torch.load

    def cpu_torch_load(*args, **kwargs):
        kwargs["map_location"] = torch.device("cpu")
        kwargs["weights_only"] = False
        return original_torch_load(*args, **kwargs)

    with patch("torch.load", cpu_torch_load):
        return joblib.load(path)


def load_models():
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    metadata = _load_serialized(MODELS_DIR / "metadata.pkl")
    bn_model = _load_serialized(MODELS_DIR / "bn_model.pkl")
    sentiment_model = _load_serialized(MODELS_DIR / "sentiment_model.pkl")
    
    if hasattr(sentiment_model, "device"):
        sentiment_model.device = torch.device("cpu")

    embedder = SentenceTransformer(str(MODELS_DIR / "sentence_transformer"))

    xgb_model = XGBClassifier()
    xgb_model.load_model(str(MODELS_DIR / "xgb_model.json"))

    nlp = spacy.load(str(MODELS_DIR / "spacy_model"))

    _CACHE = {
        "embedder": embedder,
        "xgb_model": xgb_model,
        "bn_infer": VariableElimination(bn_model),
        "sentiment_model": sentiment_model,
        "nlp": nlp,
        "domain_scores": metadata["domain_scores"],
        "clickbait_words": metadata["clickbait_words"],
        "trigger_words": metadata["trigger_words"],
    }
    return _CACHE
