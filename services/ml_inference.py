def run_ml_inference(bundle, feature_payload):
    xgb_pred = int(bundle["xgb_model"].predict(feature_payload["xgb_features"])[0])

    evidence = dict(feature_payload["evidence"])
    evidence["XGBPrediction"] = xgb_pred

    bn_result = bundle["bn_infer"].query(variables=["RealNews"], evidence=evidence)
    prob_real = float(bn_result.values[1])
    prob_fake = 1.0 - prob_real
    label = "REAL" if prob_real >= 0.5 else "FAKE"

    model_signals = dict(feature_payload["model_signals"])
    model_signals["xgb_prediction"] = xgb_pred
    model_signals["bn_evidence"] = evidence

    return {
        "label": label,
        "is_real": label == "REAL",
        "prob_real": prob_real,
        "prob_fake": prob_fake,
        "model_signals": model_signals,
    }
