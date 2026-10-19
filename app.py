import streamlit as st
from advanced_engine import (
    compute_sensationalism_score,
    extract_text_from_source,
    generate_pdf_report,
    live_web_cross_reference,
)
from claim_verifier import extract_claims
from ml_engine import RealFakeClassifier

# Page Configuration
st.set_page_config(
    page_title="True Detective — Global AI Fake News Detector",
    layout="wide",
    page_icon="🕵️‍♂️",
)

# 1. Cache the heavy ML model resource so it loads ONCE in RAM
@st.cache_resource
def get_classifier():
  return RealFakeClassifier()


classifier = get_classifier()

# Main Title & Description
st.title("🕵️‍♂️ True Detective — Global AI Fake News Detector")
st.caption(
    "Universal Real-Time Fact-Checking & Verification Engine with Multi-Modal"
    " Analysis (Text, URLs, Images & Videos)"
)

st.markdown("---")

# Input Mode Selector
input_mode = st.radio(
    "Select Input Ingestion Mode:",
    ["Plain Text", "News Article URL", "Screenshot / Image", "Video File"],
    horizontal=True,
)

raw_input = None
if input_mode == "Plain Text":
  raw_input = st.text_area(
      label="Paste news text or article statement to verify:",
      height=130,
      placeholder=(
          "e.g., Jane Doe alleges sexual assault at Cornell University"
          " fraternity..."
      ),
  )
elif input_mode == "News Article URL":
  raw_input = st.text_input(
      label="Enter News Article URL (BBC, Reuters, etc.):",
      placeholder="https://www.reuters.com/world/...",
  )
elif input_mode == "Screenshot / Image":
  raw_input = st.file_uploader(
      "Upload Image / Screenshot (PNG, JPG):", type=["png", "jpg", "jpeg"]
  )
elif input_mode == "Video File":
  raw_input = st.file_uploader(
      "Upload Video Clip (MP4, AVI, MOV):", type=["mp4", "avi", "mov"]
  )

# Execution Button
if st.button("Check Article Now", type="primary"):
  if not raw_input:
    st.warning(
        "Please provide input text, URL, image, or video before checking."
    )
  else:
    try:
      with st.spinner(
          "Extracting content and analyzing claims (processing frames/OCR)..."
      ):
        # 1. Extract text using multi-modal ingestion
        input_text = extract_text_from_source(input_mode, raw_input)

        if not input_text or len(str(input_text).strip()) < 5:
          st.error(
              "Extracted text is too short or empty. Please check your source."
          )
        else:
          # 2. Run Classification & Claim Extraction
          res = classifier.analyze("Instant Check", input_text)
          claims = extract_claims(input_text)

          # 3. Compute Sensationalism / Clickbait Score
          sensationalism = compute_sensationalism_score(input_text)

          # 4. Real-time Live Web Cross-Reference
          web_matches = live_web_cross_reference(input_text[:100])

          st.markdown("---")

          # Display Assessment Status
          status = res.get("status", "UNVERIFIED")
          confidence = res.get("confidence", 50.0)
          explanation = res.get("explanation", "")

          if status == "LIKELY TRUE":
            st.success(f"### Assessment: {status}")
          elif status == "LIKELY FALSE":
            st.error(f"### Assessment: {status}")
          else:
            st.warning(f"### Assessment: {status}")

          # Metrics Display
          col1, col2, col3 = st.columns(3)
          with col1:
            st.metric("Model Confidence", f"{confidence}%")
          with col2:
            st.metric("Sensationalism Meter", f"{sensationalism}%")
          with col3:
            st.metric("Status Signal", status)

          if explanation:
            st.info(f"**Verification Details:** {explanation}")

          # Display Extracted Claims
          if claims:
            st.subheader("🔍 Extracted Key Claims:")
            for claim in claims:
              st.write(f"• {claim}")

          # Display Live Web Cross-Reference Matches
          if web_matches:
            st.subheader("🌐 Real-Time Cross-Reference Sources:")
            for m in web_matches:
              st.markdown(f"- [{m['title']}]({m['href']})")
              if m.get("body"):
                st.caption(m["body"])

          # 5. Exportable PDF Report Generator
          st.markdown("---")
          st.subheader("📄 Download Fact-Check Audit Report")
          pdf_bytes = generate_pdf_report(
              input_text, status, confidence, sensationalism, web_matches
          )
          st.download_button(
              label="📥 Download PDF Report",
              data=pdf_bytes,
              file_name="TrueDetective_Audit_Report.pdf",
              mime="application/pdf",
          )

    except Exception as e:
      st.error(f"An error occurred during verification: {str(e)}")