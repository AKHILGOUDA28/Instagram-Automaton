import os
import json
import logging
from datetime import datetime, timezone

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL      = "openai/gpt-oss-120b"

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

def retrieve_facts(q, top_k=1): return "No facts retrieved due to temp AV block"

SYSTEM_PROMPT = """You are an elite EdTech Exam Specialist & Content Creator designing daily Current Affairs for top Indian competitive examinations (UPSC, SSC CGL/CHSL, Banking/IBPS/SBI PO/Clerk, Railways RRB, and State PSCs like TSPSC/APPSC).

I will provide today's top news articles AND a set of 'Retrieved Official Facts' from our trusted RAG database.

Your job is to select EXACTLY 6 of the highest-yield, high-probability exam updates that examiners are most likely to test in upcoming exams.

CRITICAL RULE: Use the 'Retrieved Official Facts' to ground your content. If the facts say 'No facts retrieved' or are irrelevant, use the provided news summary, ensuring absolute factual precision without hallucinations.

HIGH-PROBABILITY EXAM CONCEPTS & FOCUS AREAS (Derived from actual exam papers):
1. 🏦 Banking, Economy & Regulatory Actions:
   - RBI notifications, OMOs, repo rate, MPC surveys, NBFC CoR cancellations, SROs.
   - Financial institutions & DFIs (NaBFID, SIDBI, NABFINS, World Bank, IMF, ADB).
   - Fintech & digital payments (UPI, CBDC/e-Rupee, Credit on UPI, tokenisation).
2. 📊 Indices, Reports & Rankings:
   - Global rankings (WEF Gender Gap, QS Rankings, Henley Passport, SDG Index, etc.).
   - Exact rank of India, 1st ranked country, publishing organization, key sub-index scores.
Your job is to select EXACTLY 6 of the most high-probability updates that have a massive chance of appearing in upcoming exams.
CRITICAL RULE: Use the 'Retrieved Official Facts' to ground your content. If the Retrieved Official Facts say 'No facts retrieved' or are irrelevant, you MAY use the provided news Article Summary to generate the update, but ensure it remains strictly factual without hallucinations.

EXAM FOCUS PRIORITIES (Testbook Style Categorization):
1. Government Schemes & Policies (Outlays, target demographics)
2. Defence (Military exercises, DRDO/ISRO tests, Weapon systems)
3. Business and Economy (GDP rates, RBI mandates, World Bank loans)
4. Awards & Honours (BAFTA, Grammy, State/National Awards)
5. Days and Events (Exact themes and dates)
6. National & International Current Affairs

You must return valid JSON in this EXACT structure:
{
  "date": "22 SEPT 2026",
  "updates": [
    {
      "category": "DEFENCE",
      "headline": "Short punchy headline (max 2 lines)",
      "points": [
        "Fact-dense bullet 1 (e.g., precise names, numbers, or locations)",
        "Fact-dense bullet 2 (e.g., the core objective or theme)",
        "Fact-dense bullet 3 (e.g., historical context or related statutory body)"
      ],
      "image_url": "URL of the image from the input data exactly as provided",
      "exam_relevance": ["SSC", "UPSC", "TSPSC"],
      "question": "Which country participated with India in Exercise XYZ?",
      "answer": "France"
    }
  ],
  "caption": "Your SEO-friendly Instagram caption here",
  "hashtags": "#TSPSC #APPSC #UPSC #SSC #CurrentAffairs"
}

Rules:
1. Return exactly 6 items in the "updates" array.
2. Filter strictly for HIGH-PROBABILITY EXAM RELEVANCE.
3. The tone must be academic, data-heavy, and no-fluff (like a Testbook PDF).
4. Category must be one of: NATIONAL, INTERNATIONAL, ECONOMY, SCIENCE & TECH, DEFENCE, ENVIRONMENT, SPORTS, AWARDS, DAYS & EVENTS, APPOINTMENTS.
5. "image_url" must match the provided input exactly.
6. ONLY return the raw JSON object, no markdown blocks.
7. CRITICAL: Keep all points, headlines, and questions extremely short and concise to save output tokens.
"""

def _build_user_message(grouped_news: dict[str, list[dict]], date_str: str) -> str:
    lines = [f"Today is {date_str}. Here are today's top news articles and retrieved official RAG facts. Pick the 6 most exam-relevant updates representing core competitive exam topics:\n"]
    
    total_articles = 0
    for category, articles in grouped_news.items():
        if not articles:
            continue
        lines.append(f"\n## Category: {category}")
        # Take top 2 articles per category for balanced variety
        for i, art in enumerate(articles[:2], 1):
            if total_articles >= 14:
                break
            lines.append(f"\n### [{category}] Article {i}")
            lines.append(f"Title: {art.get('title', '')}")
            lines.append(f"Image URL: {art.get('image_url', '')}")
            if art.get("summary"):
                lines.append(f"Summary: {art['summary'][:250]}")
            
            # --- RAG RETRIEVAL ---
            query = f"{art.get('title', '')}"
            facts = retrieve_facts(query, top_k=1)
            lines.append(f"Retrieved Official Facts:\n{facts}")
            total_articles += 1
            
    lines.append("\nSelect the top 6 most high-yield exam updates across the categories above and output in the requested JSON structure.")
    return "\n".join(lines)


def summarize_news(grouped_news: dict[str, list[dict]]) -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set.")

    client = Groq(api_key=GROQ_API_KEY)
    date_str = datetime.now(timezone.utc).strftime("%d %B %Y").upper()

    user_msg = _build_user_message(grouped_news, date_str)
    log.info(f"Calling Groq ({GROQ_MODEL}) for exam-focused summarization...")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=3500,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        post_data = json.loads(raw)
    except json.JSONDecodeError as e:
        log.error(f"JSON parse failed: {e}\nRaw response:\n{raw}")
        raise

    if not post_data.get("date"):
        post_data["date"] = date_str

    log.info(f"Exam Summarization done - {len(post_data.get('updates', []))} updates generated")
    return post_data
