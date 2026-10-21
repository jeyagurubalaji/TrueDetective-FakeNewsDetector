import advanced_engine
from claim_verifier import extract_key_claims
from ml_engine import RealFakeClassifier
import streamlit as st

st.set_page_config(
    page_title="True Detective — AI Fact-Checking Engine",
    page_icon="🕵️‍♂️",
    layout="wide",
)
st.title("🕵️‍♂️ True Detective — Global AI Fact-Checking Engine")
st.markdown(
    "Advanced multi-modal verification powered by machine learning,"
    " semantic vector matching, and real-time web cross-referencing."
)
st.markdown("---")

classifier = RealFakeClassifier()

input_type = st.radio(
    "Select Input Ingestion Mode:",
    ["Plain Text", "News Article URL", "Screenshot / Image", "Video File"],
    horizontal=True,
)

raw_input = None
if input_type == "Plain Text":
  raw_input = st.text_area(
      "Paste news text or article statement to verify:", height=120
  )
elif input_type == "News Article URL":
  raw_input = st.text_input("Enter News Article URL:")
elif input_type == "Screenshot / Image":
  raw_input = st.file_uploader(
      "Upload Image / Screenshot (PNG, JPG):", type=["png", "jpg", "jpeg"]
  )
elif input_type == "Video File":
  raw_input = st.file_uploader(
      "Upload Video Clip (MP4, AVI, MOV):", type=["mp4", "avi", "mov"]
  )

if st.button("Check Article Now", type="primary"):
  if not raw_input:
    st.warning("Please provide an input source before running verification.")
  else:
    with st.spinner(
        "Running multi-modal OCR ingestion, vector similarity, and live web"
        " audit..."
    ):
      try:
        extracted_text = advanced_engine.extract_text_from_source(
            input_type, raw_input
        )
        analysis = classifier.analyze("", extracted_text)
        sensationalism = advanced_engine.compute_sensationalism_score(
            extracted_text
        )
        claims = extract_key_claims(extracted_text)
        matches = advanced_engine.live_web_cross_reference(extracted_text[:100])

        status = analysis["status"]
        confidence = analysis["confidence"]
        semantic_sim = analysis.get("semantic_similarity", 0.0)
        feature_weights = analysis.get("feature_weights", {})

        # Status Banner
        if status == "LIKELY TRUE":
          st.success(f"### Assessment: {status}")
        elif status == "MISLEADING":
          st.warning(f"### Assessment: {status}")
        elif status == "LIKELY FALSE":
          st.error(f"### Assessment: {status}")
        else:
          st.info(f"### Assessment: {status}")

        # Metrics Dashboard
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Model Confidence", f"{confidence}%")
        col2.metric("Sensationalism Meter", f"{sensationalism}%")
        col3.metric("Semantic Vector Match", f"{semantic_sim}%")
        col4.metric("Status Signal", status)

        st.info(f"**Verification Details:** {analysis['explanation']}")

        # Feature 1: SHAP Explainability & Feature Importance Dashboard
        if feature_weights:
          with st.expander(
              "📊 AI Feature Attribution & Explainability (SHAP-Style Insights)"
          ):
            st.markdown(
                "Top linguistic tokens contributing to the model classification"
                " weight:"
            )
            st.bar_chart(feature_weights)

        # Extracted Key Claims
        st.markdown("### 🔍 Extracted Key Claims:")
        for claim in claims:
          st.markdown(f"• {claim}")

        # Real-Time Cross-Reference Sources
        st.markdown("### 🌐 Real-Time Cross-Reference Sources:")
        if matches:
          for m in matches:
            st.markdown(f"- **[{m['title']}]({m['href']})**")
            st.markdown(f"  > *{m.get('body', '')[:180]}...*")
        else:
          st.markdown(
              "_No direct live search matches retrieved from current index._"
          )

        # PDF Report Download
        pdf_bytes = advanced_engine.generate_pdf_report(
            extracted_text, status, confidence, sensationalism, matches
        )
        st.download_button(
            label="📥 Download Audit Report (PDF)",
            data=pdf_bytes,
            file_name="TrueDetective_Audit_Report.pdf",
            mime="application/pdf",
        )

      except Exception as e:
        st.error(f"An error occurred during pipeline execution: {str(e)}")