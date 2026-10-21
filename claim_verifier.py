import re


def extract_key_claims(text):
  """Extracts key factual claims from input text by identifying factual assertions and key entities."""
  if not text or not isinstance(text, str):
    return ["No extractable text found in input source."]

  # Clean extra whitespaces
  clean_text = " ".join(text.split())

  # Split into sentences using punctuation delimiters
  sentences = re.split(r"(?<=[.!?])\s+", clean_text)
  claims = []

  # High-value keywords indicating core factual claims
  claim_keywords = re.compile(
      r"\b(investigators|investigation|allegations|probe|fraud|announced|court|official|police|government|dhs|ice|president|minister|found|reported|stated|confirmed|percent|\d+)\b",
      re.IGNORECASE,
  )

  for s in sentences:
    sentence = s.strip()
    if len(sentence) < 15:
      continue

    if claim_keywords.search(sentence):
      claims.append(sentence)

  # Fallback if no specific keyword matches trigger
  if not claims:
    claims = [s.strip() for s in sentences if len(s.strip()) > 20]

  # Return top 4 distinct claims or clean fallback
  unique_claims = list(dict.fromkeys(claims))
  return unique_claims[:4] if unique_claims else [clean_text]


# Backward compatibility alias
extract_claims = extract_key_claims


def verify_evidence(claims, related_articles):
  """Cross-references extracted claims against collected articles."""
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