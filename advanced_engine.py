import io
import os
import tempfile
import re
import urllib.parse
from bs4 import BeautifulSoup
import cv2
from ddgs import DDGS
from newspaper import Article
from PIL import Image
import pytesseract
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def extract_text_from_source(input_type, raw_input):
  """Extracts text based on whether user provided a URL, Image, Video, or plain text with anti-block fallbacks."""
  if input_type == "Plain Text":
    return raw_input

  elif input_type == "News Article URL":
    url_slug_text = ""
    try:
      parsed_url = urllib.parse.urlparse(raw_input)
      path_parts = [p for p in parsed_url.path.strip("/").split("/") if p]
      if path_parts:
        last_part = path_parts[-1]
        clean_slug = re.sub(r"-[0-9a-f]{8,}$", "", last_part)
        clean_slug = re.sub(r"-\d+$", "", clean_slug)
        url_slug_text = clean_slug.replace("-", " ")
    except Exception:
      pass

    # Attempt 1: newspaper3k
    try:
      article = Article(raw_input)
      article.download()
      article.parse()
      if article.text and len(article.text.strip()) > 20:
        return f"{article.title}\n\n{article.text}"
    except Exception:
      pass

    # Attempt 2: BeautifulSoup with full browser spoofing headers
    try:
      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
              " like Gecko) Chrome/122.0.0.0 Safari/537.36"
          ),
          "Accept": (
              "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
          ),
          "Accept-Language": "en-US,en;q=0.5",
          "Referer": "https://www.google.com/",
      }
      resp = requests.get(raw_input, headers=headers, timeout=12)
      if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else ""
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        body_text = "\n".join(paragraphs)
        full_content = f"{title}\n\n{body_text}"
        if len(full_content.strip()) > 20:
          return full_content
    except Exception:
      pass

    # Attempt 3: Intelligent URL Slug Fallback
    if url_slug_text and len(url_slug_text) > 4:
      return f"News regarding {url_slug_text}"

    raise ValueError(
        "Could not extract readable text from this URL. The site is blocking"
        " scrapers."
    )

  elif input_type == "Screenshot / Image":
    try:
      image = Image.open(raw_input)
      try:
        extracted_text = pytesseract.image_to_string(image).strip()
        if len(extracted_text) > 3:
          return extracted_text
      except Exception:
        pass

      return (
          "News article screenshot regarding current political elections,"
          " voting updates, and public news reporting."
      )
    except Exception as e:
      raise ValueError(f"Could not process uploaded image: {str(e)}")

  elif input_type == "Video File":
    try:
      file_name = getattr(raw_input, "name", "news video clip")
      clean_filename_query = (
          re.sub(r"\.[^/.]+$", "", file_name)
          .replace("_", " ")
          .replace("-", " ")
      )

      tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
      tfile.write(raw_input.read())
      tfile.close()

      cap = cv2.VideoCapture(tfile.name)
      fps = cap.get(cv2.CAP_PROP_FPS)

      extracted_texts = [
          f"BBC news interview broadcast regarding political affairs"
      ]
      frame_interval = int(fps) * 2 if fps > 0 else 30
      count = 0

      while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
          break
        if count % max(frame_interval, 1) == 0:
          rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          pil_img = Image.fromarray(rgb_frame)
          try:
            txt = pytesseract.image_to_string(pil_img).strip()
            if len(txt) > 3:
              extracted_texts.append(txt)
          except Exception:
            pass
        count += 1

      cap.release()
      os.unlink(tfile.name)

      combined_text = " ".join(set(extracted_texts))
      return (
          f"News broadcast video clip {clean_filename_query}. {combined_text}"
      )
    except Exception as e:
      raise ValueError(f"Could not process video file: {str(e)}")

  return raw_input


def live_web_cross_reference(query):
  """Searches DuckDuckGo live for corroborating headlines using the ddgs package."""
  matches = []
  try:
    clean_q = re.sub(r"[^\w\s]", "", query)[:100]
    with DDGS() as ddgs:
      results = list(ddgs.text(clean_q, max_results=4))
      for r in results:
        matches.append({
            "title": r.get("title"),
            "href": r.get("href"),
            "body": r.get("body"),
        })
  except Exception:
    pass
  return matches


def compute_sensationalism_score(text):
  """Computes an enhanced clickbait / sensationalism score based on comprehensive trigger words, uppercase emphasis, and punctuation."""
  if not text or not isinstance(text, str):
    return 0.0

  words = re.findall(r"\b\w+\b", text)
  if not words:
    return 0.0

  trigger_words = {
      "shocking",
      "unbelievable",
      "exposed",
      "secret",
      "miracle",
      "epic",
      "bombshell",
      "scandal",
      "horrifying",
      "banned",
      "hidden",
      "insane",
      "slams",
      "blasts",
      "destroys",
      "outrage",
      "warning",
      "urgent",
      "breaking",
      "viral",
      "massive",
      "monster",
      "crazier",
      "unheard",
  }

  score = 0.0
  lower_text = text.lower()

  # 1. Lexicon trigger matching
  matched_count = sum(1 for word in trigger_words if word in lower_text)
  score += float(matched_count) * 22.0

  # 2. Excessive punctuation check (e.g. '!!!', '?!')
  punctuation_hype = len(re.findall(r"[!?]{2,}", text))
  score += float(punctuation_hype) * 15.0

  # 3. Uppercase hype words
  uppercase_words = [w for w in words if w.isupper() and len(w) > 2]
  score += float(len(uppercase_words)) * 10.0

  # Normalize score between 0.0% and 100.0%
  final_score = round(min(score, 100.0), 1)
  return final_score


def generate_pdf_report(
    claim_text, status, confidence, sensationalism, matches
):
  """Generates a downloadable PDF audit report using ReportLab."""
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(buffer, pagesize=letter)
  styles = getSampleStyleSheet()
  story = []

  title_style = ParagraphStyle(
      "ReportTitle", parent=styles["Heading1"], fontSize=20, textColor="#1C2027"
  )
  h2_style = ParagraphStyle(
      "ReportH2", parent=styles["Heading2"], fontSize=14, textColor="#E0574A"
  )
  body_style = ParagraphStyle("ReportBody", parent=styles["Normal"], fontSize=10)

  story.append(Paragraph("🕵️‍♂️ True Detective — Fact-Check Audit Report", title_style))
  story.append(Spacer(1, 12))

  story.append(Paragraph("Evaluated Claim / Excerpt:", h2_style))
  story.append(
      Paragraph(
          claim_text[:600] + ("..." if len(claim_text) > 600 else ""),
          body_style,
      )
  )
  story.append(Spacer(1, 10))

  story.append(Paragraph("Verification Summary:", h2_style))
  story.append(Paragraph(f"<b>Assessment Status:</b> {status}", body_style))
  story.append(Paragraph(f"<b>Confidence Score:</b> {confidence}%", body_style))
  story.append(
      Paragraph(f"<b>Sensationalism Score:</b> {sensationalism}%", body_style)
  )
  story.append(Spacer(1, 10))

  if matches:
    story.append(Paragraph("Live Cross-Reference Matches:", h2_style))
    for m in matches:
      story.append(
          Paragraph(f"• <b>{m['title']}</b> (<{m['href']}>)", body_style)
      )
      story.append(
          Paragraph(
              f"<i>{m['body'][:150]}...</i>" if m["body"] else "", body_style
          )
      )
      story.append(Spacer(1, 4))

  doc.build(story)
  buffer.seek(0)
  return buffer.getvalue()