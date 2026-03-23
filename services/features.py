import numpy as np


def normalize_domain(domain_url):
    domain = domain_url.strip().lower()
    domain = domain.replace("https://", "").replace("http://", "")
    domain = domain.split("/")[0]
    domain = domain.replace("www.", "")
    return domain


def sentiment_score(sentiment_model, text):
    result = sentiment_model(text[:512])[0]
    if result["label"] == "POSITIVE":
        return float(result["score"])
    return -float(result["score"])


def clickbait_score(clickbait_words, text):
    text_lower = text.lower()
    score = 0
    for word in clickbait_words:
        if word in text_lower:
            score += 1
    return score


def trigger_density(trigger_words, text):
    words = text.lower().split()
    count = sum(word in trigger_words for word in words)
    return count / max(len(words), 1)


def writing_style_score(text):
    length = len(text.split())
    exclam = text.count("!")
    caps = sum(1 for w in text.split() if w.isupper())
    return (exclam + caps) / max(length, 1)


def fact_signal(nlp, text):
    doc = nlp(text)
    entities = [ent.label_ for ent in doc.ents]
    return int("PERSON" in entities or "ORG" in entities or "GPE" in entities)


def build_feature_payload(bundle, title, domain_url, tweet_count):
    domain = normalize_domain(domain_url)
    tweets = int(tweet_count)

    credibility = float(bundle["domain_scores"].get(domain, 0.5))
    sentiment = sentiment_score(bundle["sentiment_model"], title)
    clickbait = clickbait_score(bundle["clickbait_words"], title)
    trigger = trigger_density(bundle["trigger_words"], title)
    writing = writing_style_score(title)
    fact = fact_signal(bundle["nlp"], title)

    emb = bundle["embedder"].encode(title)
    extra = np.array(
        [
            credibility,
            tweets,
            sentiment,
            clickbait,
            trigger,
            writing,
            fact,
        ]
    )
    xgb_features = np.hstack([emb, extra]).reshape(1, -1)

    evidence = {
        "Credibility": 1 if credibility > 0.75 else 0,
        "TweetSignal": 1 if tweets > 50 else 0,
        "Sentiment": 1 if sentiment > 0 else 0,
        "Clickbait": 1 if clickbait > 0 else 0,
        "TriggerWords": 1 if trigger > 0.02 else 0,
        "WritingStyle": 1 if writing > 0.05 else 0,
        "FactSignal": int(fact),
    }

    model_signals = {
        "domain": domain,
        "credibility_score": credibility,
        "tweet_count": tweets,
        "sentiment_score": sentiment,
        "clickbait_score": clickbait,
        "trigger_density": trigger,
        "writing_style_score": writing,
        "fact_signal": fact,
    }

    return {
        "xgb_features": xgb_features,
        "evidence": evidence,
        "model_signals": model_signals,
    }
