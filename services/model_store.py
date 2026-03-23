import pickle
from pathlib import Path

import spacy
from pgmpy.inference import VariableElimination
from sentence_transformers import SentenceTransformer
from xgboost import XGBClassifier


ROOT_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT_DIR / "training" / "saved_models"


_CACHE = None


def load_models():
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    with open(MODELS_DIR / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)

    with open(MODELS_DIR / "bn_model.pkl", "rb") as f:
        bn_model = pickle.load(f)

    with open(MODELS_DIR / "sentiment_model.pkl", "rb") as f:
        sentiment_model = pickle.load(f)

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
