# 🕵️‍♂️ True Detective — Global AI Fact-Checking & Misinformation Engine

**True Detective** is an AI-powered fact-checking and misinformation detection platform that analyzes news content, verifies factual claims using live web sources, evaluates sensationalism, and provides explainable analysis.

The system supports multiple input formats including text, news article URLs, images, and video files.

---

## 🌟 Key Features

- **Multi-Modal Fact Checking** – Analyze plain text, news URLs, screenshots/images, and video files.
- **Live Web Verification** – Cross-references claims with live search results and Google News RSS feeds.
- **Semantic Similarity Analysis** – Uses TF-IDF vectorization and cosine similarity to compare claims with web sources.
- **Claim Extraction** – Identifies and analyzes important factual statements from submitted content.
- **Sensationalism Detection** – Detects clickbait language, excessive punctuation, ALL-CAPS text, and emotional exaggeration.
- **Explainable AI** – Provides token-level importance and model confidence information.
- **OCR Support** – Extracts text from screenshots and images using Tesseract OCR.
- **Video Analysis** – Samples video frames and processes available speech/transcribed content.
- **PDF Audit Reports** – Generates downloadable fact-checking reports using ReportLab.
- **Live Deployment** – Available as a Streamlit web application.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Language | Python 3.10+ |
| Frontend / UI | Streamlit |
| Machine Learning | Scikit-learn |
| Data Processing | NumPy, Pandas |
| NLP | TF-IDF, Cosine Similarity |
| Web Search | DuckDuckGo Search (`ddgs`), Google News RSS |
| Web Scraping | BeautifulSoup, Newspaper3k, Requests |
| OCR | PyTesseract |
| Computer Vision | OpenCV, Pillow |
| PDF Generation | ReportLab |
| Deployment | Streamlit Community Cloud |
| CI/CD | GitHub Actions |

---

## 📂 Project Structure

```text
TrueDetective-FakeNewsDetector/
│
├── app.py                  # Streamlit application and user interface
├── ml_engine.py            # ML classification and web similarity engine
├── claim_verifier.py       # Claim extraction and verification logic
├── advanced_engine.py      # OCR, video, URL processing and PDF generation
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
│
└── .github/
    └── workflows/
        └── keep_alive.yml  # Automated application health workflow
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jeyagurubalaji/TrueDetective-FakeNewsDetector.git
cd TrueDetective-FakeNewsDetector
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

For image and video OCR features, make sure **Tesseract OCR** is installed and available in your system PATH.

### 3. Run the Application

```bash
streamlit run app.py
```

The application will be available locally at:

```text
http://localhost:8501
```

---

## 🚀 How It Works

```text
User Input
    │
    ├── Text
    ├── News URL
    ├── Image / Screenshot
    └── Video
          │
          ▼
    Content Extraction
          │
          ▼
    Claim Identification
          │
          ▼
    Live Web Search
          │
          ▼
    TF-IDF + Similarity Analysis
          │
          ▼
    Sensationalism Analysis
          │
          ▼
    AI Assessment
          │
          ├── LIKELY TRUE
          ├── MISLEADING
          └── LIKELY FALSE
          │
          ▼
    Explainability & PDF Report
```

---

## 📊 Analysis Output

True Detective provides:

- Verification status
- Model confidence
- Source comparison
- Semantic similarity scores
- Sensationalism score
- Claim-level analysis
- Explainable token importance
- Downloadable PDF audit report

> **Note:** AI-generated fact-checking results are probabilistic assessments and should be verified against authoritative primary sources for high-stakes claims.

---

## 🌐 Live Application

Try the deployed application:

**[🚀 Launch True Detective](https://truedetective.streamlit.app/)**

---

## 📄 License

MIT License © 2026 Jeyagurubalaji P. All rights reserved