import re
from ddgs import DDGS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RealFakeClassifier:

  def __init__(self):
    pass

  def clean_query(self, text):
    stop_words = {
        "in",
        "the",
        "and",
        "to",
        "of",
        "a",
        "for",
        "on",
        "with",
        "as",
        "by",
        "at",
        "html",
        "www",
        "com",
    }
    words = re.findall(r"\b[A-Za-z0-9]+\b", text)
    filtered = [w for w in words if w.lower() not in stop_words]
    return " ".join(filtered[:8])

  def analyze(self, title, text):
    full_text = f"{title} {text}".strip()
    clean_q = self.clean_query(full_text)

    if not clean_q or len(clean_q.strip()) < 3:
      return {
          "status": "UNVERIFIED",
          "confidence": 50.0,
          "explanation": "Query too short to verify against live news sources.",
      }

    matches = []
    try:
      with DDGS() as ddgs:
        results = list(ddgs.text(clean_q, max_results=6))
        for r in results:
          matches.append({
              "title": r.get("title", ""),
              "body": r.get("body", ""),
          })
    except Exception as e:
      print(f"Search error: {e}")

    if not matches:
      return {
          "status": "UNVERIFIED",
          "confidence": 50.0,
          "explanation": "Unable to connect to live search indexes.",
      }

    headlines = [m["title"] + " " + m["body"] for m in matches]
    corpus = [full_text] + headlines

    try:
      vectorizer = TfidfVectorizer().fit_transform(corpus)
      vectors = vectorizer.toarray()
      claim_vector = vectors[0].reshape(1, -1)
      headline_vectors = vectors[1:]

      similarities = cosine_similarity(claim_vector, headline_vectors)[0]
      max_idx = similarities.argmax()
      max_sim = similarities[max_idx]
      best_match = matches[max_idx]["title"]

      # Robust threshold for live search corroboration
      if max_sim >= 0.18:
        confidence = round(min(80.0 + (max_sim * 25.0), 98.0), 1)
        return {
            "status": "LIKELY TRUE",
            "confidence": confidence,
            "explanation": (
                f"Corroborated by live web search reporting: '{best_match}'"
            ),
        }
      elif 0.08 <= max_sim < 0.18:
        return {
            "status": "MISLEADING",
            "confidence": 72.0,
            "explanation": (
                f"Related news found, but context/details differ:"
                f" '{best_match}'"
            ),
        }
      else:
        return {
            "status": "LIKELY FALSE",
            "confidence": 85.0,
            "explanation": (
                "No matching live reporting found across trusted web indexes."
            ),
        }
    except Exception as ex:
      return {
          "status": "UNVERIFIED",
          "confidence": 50.0,
          "explanation": f"Analysis error: {str(ex)}",
      }