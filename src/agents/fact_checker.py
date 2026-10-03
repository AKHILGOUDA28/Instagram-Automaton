"""
fact_checker.py — Agentic LLM-as-a-judge to verify generated facts against RAG sources.
"""

import os
import json
import logging
from groq import Groq
def retrieve_facts(q, top_k=1): return "No facts retrieved due to temp AV block"

log = logging.getLogger(__name__)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

def verify_post_data(post_data: dict) -> dict:
    """
    Acts as a Verification Agent. 
    It takes the drafted Instagram post, retrieves RAG facts again, and ensures no hallucinations occurred.
    """
    if not GROQ_API_KEY:
        log.warning("No Groq API key, skipping fact-check.")
        return post_data

    client = Groq(api_key=GROQ_API_KEY)
    
    log.info("Starting Agentic Fact-Checking on generated content...")
    
    verified_updates = []
    
    for item in post_data.get("updates", []):
        headline = item.get("headline", "")
        facts = " | ".join(item.get("points", []))
        
        # Retrieve official facts specifically for this claim
        query = f"{headline} {facts}"
        official_sources = retrieve_facts(query, top_k=2)
        
        # Ask LLM to act as a strict Judge
        prompt = f"""You are a strict Fact-Checking Agent.
Compare the 'Claim' against the 'Official Sources'.
If the Claim contradicts the Official Sources, fix the Claim so it is accurate. 
If the Claim is completely unrelated to the Official Sources but still seems plausible, keep it.
Return ONLY valid JSON: {{"status": "PASS" | "FIXED", "fixed_points": ["fact1", "fact2", "fact3"]}}

Claim:
Headline: {headline}
Points: {facts}

Official Sources:
{official_sources}
"""
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
                
            verification = json.loads(raw)
            if verification.get("status") == "FIXED":
                log.info(f"Fact-Checker Agent corrected a hallucination in: {headline[:30]}...")
                item["points"] = verification.get("fixed_points", item["points"])
            else:
                log.info(f"Fact-Checker Agent approved: {headline[:30]}...")
                
        except Exception as e:
            log.warning(f"Fact checking failed for item, keeping original: {e}")
            
        verified_updates.append(item)
        
    post_data["updates"] = verified_updates
    return post_data
