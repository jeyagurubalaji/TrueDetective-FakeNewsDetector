import re


def extract_key_claims(text):
  """Extracts key factual claims using sentence splitters and numeric/entity identifiers."""
  if not text or not isinstance(text, str):
    return ["No extractable text found in input source."]

  sentences = re.split(r"(?<=[.!?]) +", text)
  claims = []

  for s in sentences:
    clean_s = s.strip()
    # Highlight claims containing numbers, percentages, or high-value assertion verbs
    if re.search(
        r"\d+|percent|announced|discovered|claimed|proved|official|referendum|vote|court|president|minister",
        clean_s,
        re.IGNORECASE,
    ):
      if len(clean_s) > 15:
        claims.append(clean_s)

  # Fallback if no specific keyword matches are found
  if not claims:
    for s in sentences:
      clean_s = s.strip()
      if len(clean_s) > 20:
        claims.append(clean_s)

  return (
      claims[:4]
      if claims
      else [text[:120] + ("..." if len(text) > 120 else "")]
  )


# Alias for backward compatibility
extract_claims = extract_key_claims


def verify_evidence(claims, related_articles):
  """Cross-references extracted claims against other collected articles."""
  supporting = 0
  contradicting = 0

  for claim in claims:
    claim_words = set(re.findall(r"\w+", claim.lower()))
    for art in related_articles:
      art_words = set(re.findall(r"\w+", art.get("description", "").lower()))
      intersection = claim_words.intersection(art_words)

      if len(intersection) >= 4:
        supporting += 1
      elif len(intersection) == 2:
        contradicting += 1

  return {
      "supporting_sources": max(1, supporting),
      "contradicting_sources": contradicting,
      "evidence_quality": (
          "Strong" if supporting > 2 else "Insufficient Evidence"
      ),
  }