import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ==================================================
# ENVIRONMENT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")


# ==================================================
# GROQ CLIENT
# ==================================================

MODEL_NAME = "openai/gpt-oss-120b"

client = Groq(api_key=API_KEY)


# ==================================================
# SYSTEM PROMPT
# ==================================================

SYSTEM_PROMPT = """You are a warm, friendly medical report explainer — like a knowledgeable friend
who happens to understand medicine. Your job is to help patients truly UNDERSTAND their reports,
not just see numbers.

STRICT RULES:
1. NEVER diagnose any condition. Never say "you have X disease".
2. ALWAYS recommend consulting a doctor for abnormal findings.
3. Use simple everyday language (Grade 6-8 reading level).
4. Be reassuring, warm and honest.
5. You are an educational tool ONLY, not a medical professional.
6. For every finding — whether normal, borderline or abnormal — give a rich explanation.

For EVERY test finding you MUST explain:
- What this test actually measures in the body (in simple words)
- What the result means for this specific patient
- If LOW: what happens in the body when this is low, common reasons why,
  how it might make someone feel, and what lifestyle or dietary factors can help
- If HIGH: what happens in the body when this is high, common reasons why,
  how it might make someone feel, and what to watch out for
- If NORMAL: reassure the patient and explain why this is a good sign
- Any relevant food, nutrition, or lifestyle connection
- Whether they need to see a doctor and what type of specialist

Respond ONLY with a valid JSON object in this exact format, no extra text before or after:

{
  "summary": "3-4 sentence warm and clear overview of the overall report in plain English",
  "overall_health_message": "An encouraging 2-3 sentence message about what this report says about their overall health",
  "findings": [
    {
      "test_name": "Name of the test",
      "value": "The result value with units",
      "normal_range": "The normal range for this test",
      "status": "normal or borderline or abnormal",
      "what_it_measures": "1-2 sentences explaining what this test measures in the body in simple language",
      "what_your_result_means": "2-3 sentences explaining specifically what THIS patient's result means",
      "body_impact": "2-3 sentences on how this level affects the body and how the patient might feel",
      "lifestyle_tip": "1-2 practical sentences on food, lifestyle or habits related to this finding",
      "action_needed": "What the patient should do about this specific finding"
    }
  ],
  "nutrition_summary": "2-3 sentences summarizing any key nutritional deficiencies or excesses found and simple dietary suggestions",
  "doctor_advice": "Clear advice on whether/how urgently to see a doctor, what type of specialist and what to tell them",
  "urgency": "routine or soon or urgent",
  "disclaimer": "Standard reminder that this is educational only and not a diagnosis"
}"""


# ==================================================
# EXPLAIN MEDICAL REPORT
# ==================================================

def explain_medical_report(report_text: str) -> dict:

    if not report_text or not report_text.strip():
        raise ValueError("Please provide medical report text.")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    "Please explain this medical report in detail:\n\n"
                    + report_text
                )
            }
        ],
        temperature=0.3,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError("Groq returned an empty response.")

    response_text = response_text.strip()

    # Remove Markdown code fences if returned
    if response_text.startswith("```"):
        lines = response_text.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response_text = "\n".join(lines).strip()

    # Parse JSON response
    try:
        result = json.loads(response_text)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON returned by Groq: {error}"
        ) from error

    if not isinstance(result, dict):
        raise ValueError("AI response is not a valid JSON object.")

    return result