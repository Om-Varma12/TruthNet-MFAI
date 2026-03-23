from dotenv import load_dotenv
from services.features import build_feature_payload, normalize_domain
from services.llm_service import build_support_with_llm
from services.ml_inference import run_ml_inference
from services.model_store import load_models
from pprint import pprint

load_dotenv()


def invokePipeline(title, domain_url, tweet_count):
    bundle = load_models()
    domain = normalize_domain(domain_url)

    feature_payload = build_feature_payload(
        bundle=bundle,
        title=title,
        domain_url=domain,
        tweet_count=tweet_count,
    )

    ml_result = run_ml_inference(bundle=bundle, feature_payload=feature_payload)
    llm_part = build_support_with_llm(title=title, domain=domain, ml_result=ml_result)

    support = {
        "label": ml_result["label"],
        "prob_real": ml_result["prob_real"],
        "prob_fake": ml_result["prob_fake"],
        "model_signals": ml_result["model_signals"],
        "generated_query": llm_part["generated_query"],
        "search_results": llm_part["search_results"],
        "reason": llm_part["reason"],
    }

    return {
        "is_real": ml_result["is_real"],
        "support": support,
    }
    
    
# title = "USA confirms that covid was all fake and none of that ever existed."
# domain = "reuters.com"
# tweets = 500
    
# pprint(invokePipeline(
#     title=title,
#     domain_url=domain,
#     tweet_count=tweets
# ))