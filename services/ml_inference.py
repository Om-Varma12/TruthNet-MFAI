def run_ml_inference(bundle, feature_payload):
    xgb_pred = int(bundle["xgb_model"].predict(feature_payload["xgb_features"])[0])

    evidence = dict(feature_payload["evidence"])
    evidence["XGBPrediction"] = xgb_pred

    print(f"[DEBUG] XGBPrediction: {xgb_pred}")
    print(f"[DEBUG] Evidence: {evidence}")

    bn_result = bundle["bn_infer"].query(variables=["RealNews"], evidence=evidence)

    print(f"[DEBUG] BN Result: {bn_result}")
    
    prob_real = float(bn_result.values[1])
    prob_fake = 1.0 - prob_real
    label = "REAL" if prob_real > 0.5 else "FAKE"

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


# if __name__ == "__main__":
#     from services.model_store import load_models
#     from services.features import build_feature_payload

#     print("[DEBUG] Loading models...")
#     bundle = load_models()

#     # Demo parameters
#     demo_title = "Scientists confirm that vaccines alter human DNA permanently"
#     demo_domain = "reuters.com"
#     demo_tweets = 500

#     print(f"[DEBUG] Title: {demo_title}")
#     print(f"[DEBUG] Domain: {demo_domain}")
#     print(f"[DEBUG] Tweet count: {demo_tweets}")

#     feature_payload = build_feature_payload(
#         bundle=bundle,
#         title=demo_title,
#         domain_url=demo_domain,
#         tweet_count=demo_tweets,
#     )

#     print(f"[DEBUG] xgb_features shape: {feature_payload['xgb_features'].shape}")
#     print(f"[DEBUG] evidence: {feature_payload['evidence']}")
#     print(f"[DEBUG] model_signals: {feature_payload['model_signals']}")

#     result = run_ml_inference(bundle=bundle, feature_payload=feature_payload)

#     print("\n========== FINAL RESULT ==========")
#     print(f"Label      : {result['label']}")
#     print(f"Is Real    : {result['is_real']}")
#     print(f"P(real)    : {result['prob_real']:.4f}")
#     print(f"P(fake)    : {result['prob_fake']:.4f}")
#     print(f"Model Sig  : {result['model_signals']}")
