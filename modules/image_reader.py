import json
import re
import base64
import time
from openai import OpenAI
from PIL import Image
import io

EXTRACTION_PROMPT = """You are analysing a corrected student answer sheet image.

The teacher has already marked this paper. Look for:
- Ticks or correct marks = question answered correctly
- Crosses, red marks, corrections, crossed-out text = question answered incorrectly

For EACH question on the sheet:
1. Find the question number (Q1, Q2, 1., 2., etc.)
2. READ the question text to understand what topic/concept it is testing
3. Decide if the answer is correct or incorrect based on teacher marks
4. If incorrect, describe the mistake in 3-5 words
5. Name the concept being tested (e.g. Fractions, Algebra, Newton Laws)

Return ONLY raw JSON. No explanation. No markdown. Just the JSON object.

Format:
{
  "questions": {
    "Q1": { "concept": "Fractions", "correct": false, "mistake": "added denominators incorrectly" },
    "Q2": { "concept": "Algebra", "correct": true, "mistake": null }
  }
}
"""


def _parse_json(text: str) -> dict:
    clean = text.strip()
    clean = re.sub(r"^```[a-z]*\n?", "", clean)
    clean = re.sub(r"\n?```$", "", clean)
    clean = clean.strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", clean)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {"questions": {}}


def _image_to_base64(image_file) -> tuple[str, str]:
    image_bytes = image_file.read()
    image       = Image.open(io.BytesIO(image_bytes))
    # Convert to PNG for consistency
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b64, "image/png"


def read_answer_sheet(image_file, api_key: str, paper_number: int = 1) -> dict:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    b64, mime = _image_to_base64(image_file)

    # Free vision models on OpenRouter
    models_to_try = [
        "nvidia/nemotron-nano-12b-v2-vl:free",
        "google/gemma-4-26b-a4b-it:free",
        "google/gemma-4-31b-it:free",
    ]

    all_errors = []

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": EXTRACTION_PROMPT},
                            {"type": "image_url",
                             "image_url": {"url": f"data:{mime};base64,{b64}"}},
                        ],
                    }
                ],
                max_tokens=1024,
            )
            raw    = response.choices[0].message.content
            parsed = _parse_json(raw)

            if parsed.get("questions"):
                return {
                    "paper":     paper_number,
                    "questions": parsed["questions"],
                    "model":     model,
                }
            else:
                all_errors.append(f"{model}: empty response — {raw[:80]}")
                continue

        except Exception as e:
            all_errors.append(f"{model}: {str(e)[:120]}")
            time.sleep(2)
            continue

    return {
        "paper":     paper_number,
        "questions": {},
        "error":     " | ".join(all_errors),
    }


def read_all_sheets(image_files: list, api_key: str, progress_callback=None) -> list:
    results = []
    total   = len(image_files)
    for i, f in enumerate(image_files, start=1):
        result = read_answer_sheet(f, api_key, paper_number=i)
        results.append(result)
        if i < total:
            time.sleep(3)
        if progress_callback:
            progress_callback(i, total)
    return results
