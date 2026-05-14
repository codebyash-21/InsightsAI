# 🎓 InsightAI — Concept Intelligence for Teachers

> "Marks tell you the score. InsightAI tells you the story."

InsightAI is an AI-powered tool that helps teachers identify which concepts their students are struggling with — just by uploading photos of corrected answer sheets.

---

## 🚀 What It Does

Upload 5-6 photos of corrected answer sheets → AI reads every paper → Dashboard shows which concepts to re-teach next class.

No manual data entry. No spreadsheets. Just upload and get insights.

---

## ✨ Features

- 📸 Upload photos of corrected answer sheets (JPG, PNG)
- 🤖 AI reads handwriting, ticks and crosses automatically
- 📊 Ranked concept weakness dashboard
- 🗺️ Paper × Question heatmap
- 🍩 Mistake type distribution chart
- 🔴 "Re-teach these next class" alert

---

## 🛠️ Tech Stack

| Layer | Tool | Cost |
|---|---|---|
| Language | Python 3.11+ | Free |
| UI | Streamlit | Free |
| AI / Vision | OpenRouter (Nemotron VL) | Free |
| Data | Pandas | Free |
| Charts | Plotly | Free |
| Deployment | Streamlit Community Cloud | Free |

---

## ⚡ Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/codebyash-21/InsightAI.git
cd InsightAI
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Get a free API key**
- Go to [openrouter.ai](https://openrouter.ai)
- Sign up (no credit card needed)
- Create an API key

**5. Add your key**

Copy `.env.example` to `.env` and add your key:
