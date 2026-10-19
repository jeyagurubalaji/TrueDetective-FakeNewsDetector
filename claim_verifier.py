import re

def extract_claims(text):
    """Extracts factual claims using key sentence splitters and numeric/entity identifiers."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    claims = []

    for s in sentences:
        # Highlight claims containing numbers, percentages, or high-value assertion verbs
        if re.search(r'\d+|percent|announced|discovered|claimed|proved|official', s, re.IGNORECASE):
            if len(s.strip()) > 20:
                claims.append(s.strip())

    return claims if claims else [text[:100] + "..."]

def verify_evidence(claims, related_articles):
    """Cross-references extracted claims against other collected articles."""
    supporting = 0
    contradicting = 0

    for claim in claims:
        claim_words = set(re.findall(r'\w+', claim.lower()))
        for art in related_articles:
            art_words = set(re.findall(r'\w+', art.get('description', '').lower()))
            intersection = claim_words.intersection(art_words)

            if len(intersection) >= 4:
                supporting += 1
            elif len(intersection) == 2:
                contradicting += 1

    return {
        "supporting_sources": max(1, supporting),
        "contradicting_sources": contradicting,
        "evidence_quality": "Strong" if supporting > 2 else "Insufficient Evidence"
    }