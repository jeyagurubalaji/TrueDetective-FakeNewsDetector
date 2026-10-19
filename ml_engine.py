import re
import time
import urllib.parse
from ddgs import DDGS
import feedparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RealFakeClassifier:

  def __init__(self):
    pass

  def clean_query(self, text):
    stop_words = {
        'in',
        'the',
        'and',
        'to',
        'of',
        'a',
        'for',
        'on',
        'with',
        'as',
        'by',
        'at',
        'html',
        'www',
        'com',
    }
    words = re.findall(r'\b[A-Za-z0-9]+\b', text)
    filtered = [w for w in words if w.lower() not in stop_words]
    return ' '.join(filtered[:8])

  def fetch_live_matches(self, query):
    matches = []

    # Method 1: DuckDuckGo with retry logic
    for attempt in range(2):
      try:
        with DDGS() as ddgs:
          results = list(ddgs.text(query, max_results=6))
          for r in results:
            matches.append(
                {'title': r.get('title', ''), 'body': r.get('body', '')}
            )
          if matches:
            return matches
      except Exception:
        time.sleep(1)

    # Method 2: Fallback to Google News RSS feed if DDGS rate-limits
    try:
      encoded_q = urllib.parse.quote(query)
      rss_url = f'https://news.google.com/rss/search?q={encoded_q}&hl=en-US&gl=US&ceid=US:en'
      feed = feedparser.parse(rss_url)
      for entry in feed.entries[:6]:
        matches.append({'title': entry.get('title', ''), 'body': ''})
    except Exception:
      pass

    return matches

  def analyze(self, title, text):
    full_text = f'{title} {text}'.strip()
    clean_q = self.clean_query(full_text)

    if not clean_q or len(clean_q.strip()) < 3:
      return {
          'status': 'UNVERIFIED',
          'confidence': 50.0,
          'explanation': 'Query too short to verify against live news sources.',
      }

    matches = self.fetch_live_matches(clean_q)

    if not matches:
      return {
          'status': 'UNVERIFIED',
          'confidence': 50.0,
          'explanation': (
              'No live search reporting found across trusted web indexes.'
          ),
      }

    headlines = [m['title'] + ' ' + m['body'] for m in matches]
    corpus = [full_text] + headlines

    try:
      vectorizer = TfidfVectorizer().fit_transform(corpus)
      vectors = vectorizer.toarray()
      claim_vector = vectors[0].reshape(1, -1)
      headline_vectors = vectors[1:]

      similarities = cosine_similarity(claim_vector, headline_vectors)[0]
      max_idx = similarities.argmax()
      max_sim = similarities[max_idx]
      best_match = matches[max_idx]['title']

      # Corroboration thresholds
      if max_sim >= 0.15:
        confidence = round(min(82.0 + (max_sim * 22.0), 98.0), 1)
        return {
            'status': 'LIKELY TRUE',
            'confidence': confidence,
            'explanation': (
                f"Corroborated by live web search reporting: '{best_match}'"
            ),
        }
      elif 0.07 <= max_sim < 0.15:
        return {
            'status': 'MISLEADING',
            'confidence': 72.0,
            'explanation': (
                f'Related news found, but details vary: \'{best_match}\''
            ),
        }
      else:
        return {
            'status': 'LIKELY FALSE',
            'confidence': 85.0,
            'explanation': (
                'No corroborating live reporting found for this specific'
                ' claim.'
            ),
        }
    except Exception as ex:
      return {
          'status': 'UNVERIFIED',
          'confidence': 50.0,
          'explanation': f'Analysis error: {str(ex)}',
      }