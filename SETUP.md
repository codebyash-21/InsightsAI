# InsightAI — Setup Guide

## Folder Structure

InsightAI/
├── app.py
├── requirements.txt
├── .env.example
├── SETUP.md
├── modules/
│ ├── **init**.py
│ ├── image_reader.py
│ └── insights.py

---

## Step 1 — Get a Free Gemini API Key

1. Go to **https://aistudio.google.com**
2. Sign in with your Google account (no credit card needed)
3. Click **Get API Key → Create API Key**
4. Copy the key (starts with `AIza...`)

---

## Step 2 — Set Up in VS Code

Open the terminal in VS Code (Ctrl + `) and run:

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

---

## Step 3 — Run the App

    streamlit run app.py

Your browser opens at http://localhost:8501

---

## Step 4 — Using the App

1. Paste your Gemini API key in the sidebar
2. Upload 5–6 photos of corrected answer sheets (JPG, PNG)
3. Fill in the concept map like this:
   Q1=Fractions
   Q2=Algebra
   Q3=Newton's Laws
4. Click **Analyse Papers**
5. See which concepts your class is struggling with

---

## Tips for Best Results

- Photos should be clear and well-lit
- Make sure teacher corrections (ticks/crosses) are visible
- Each image = one student's answer sheet
- Concept map must match the question numbers on the sheet

---

## Troubleshooting

| Problem             | Fix                                                  |
| ------------------- | ---------------------------------------------------- |
| ModuleNotFoundError | Run pip install -r requirements.txt with venv active |
| Invalid API key     | Re-copy from aistudio.google.com                     |
| App shows no data   | Make sure images are clear and well-lit              |
| Streamlit not found | Activate venv before running                         |
