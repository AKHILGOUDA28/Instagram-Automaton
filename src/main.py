"""
main.py
───────
Orchestrator — runs the full Current Affairs → Instagram pipeline.

Usage:
  python src/main.py            # full run (collect → summarize → generate → upload → publish)
  python src/main.py --dry-run  # stop before publishing (saves image locally only)
  python src/main.py --test-image  # generate image from sample data, no API calls
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.news_collector  import collect_todays_news
from src.summarizer      import summarize_news
from src.image_generator import generate_image
from src.uploader        import upload_image_to_github
from src.publisher       import publish_to_instagram
from src.agents.fact_checker import verify_post_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

SAMPLE_POST_DATA = {
    "date": datetime.now(timezone.utc).strftime("%d %B %Y"),
    "categories": [
        {
            "name": "India", "emoji": "🇮🇳",
            "items": [{
                "headline": "PM launches new digital infrastructure scheme",
                "summary": "The Prime Minister announced a ₹10,000 crore digital infrastructure scheme targeting rural areas.",
                "key_points": ["₹10,000 crore allocated", "Targets rural connectivity", "500 districts to benefit"],
                "why_it_matters": "Key for GS-II Governance and Social Justice topics."
            }]
        },
        {
            "name": "Economy", "emoji": "💰",
            "items": [{
                "headline": "RBI holds repo rate steady at 6.5 percent",
                "summary": "The RBI Monetary Policy Committee voted 5-1 to keep the repo rate unchanged at 6.5%.",
                "key_points": ["Repo rate: 6.5%", "GDP forecast raised to 7.2%", "CPI inflation within target"],
                "why_it_matters": "Essential for Banking Awareness and Economy sections."
            }]
        },
        {
            "name": "World", "emoji": "🌎",
            "items": [{
                "headline": "UN General Assembly opens 81st session in New York",
                "summary": "World leaders gather for the 81st UNGA session with focus on climate and Global South issues.",
                "key_points": ["India raises climate agenda", "PM addresses UNGA", "Focus on Global South"],
                "why_it_matters": "Important for International Relations and Organisations."
            }]
        },
        {
            "name": "Science & Tech", "emoji": "🔬",
            "items": [{
                "headline": "ISRO successfully tests CE-20 cryogenic engine",
                "summary": "ISRO tested its CE-20 cryogenic engine as part of preparations for the Gaganyaan mission.",
                "key_points": ["CE-20 engine tested", "Gaganyaan mission prep", "Human spaceflight by 2025"],
                "why_it_matters": "Important for Science & Technology prelims questions."
            }]
        },
    ],
    "instagram_caption": (
        "📰 Daily Current Affairs | {date}\n\n"
        "🇮🇳 India: PM launches digital infrastructure scheme\n"
        "💰 Economy: RBI holds repo rate at 6.5%\n"
        "🌎 World: UNGA 81st session opens\n"
        "🔬 Science: ISRO tests CE-20 engine\n\n"
        "Follow for daily current affairs! 📚\n\n"
        "#CurrentAffairs #UPSC #SSC #DailyGK #GK #India #IAS #TGPSC"
    ),
    "hashtags": ["#CurrentAffairs", "#UPSC", "#SSC", "#DailyGK", "#GK", "#India"]
}


# ── Pipeline steps ─────────────────────────────────────────────────────────────

def step_collect() -> dict:
    log.info("━" * 60)
    log.info("STEP 1 — Collecting today's news")
    log.info("━" * 60)
    news = collect_todays_news(max_per_category=2)
    total = sum(len(v) for v in news.values())
    log.info(f"Collected {total} fresh articles across {len(news)} categories")
    return news


def step_summarize(news: dict) -> dict:
    log.info("━" * 60)
    log.info("STEP 2 — Summarizing with Groq LLM")
    log.info("━" * 60)
    post_data = summarize_news(news)
    log.info(f"Post data ready — {len(post_data.get('categories', []))} categories")
    return post_data


def step_generate_image(post_data: dict) -> Path:
    log.info("━" * 60)
    log.info("STEP 3 — Generating Instagram image")
    log.info("━" * 60)
    image_path = generate_image(post_data)
    log.info(f"Image saved: {image_path}")
    return image_path


def step_upload(image_path: Path) -> str:
    log.info("━" * 60)
    log.info("STEP 4 — Uploading image to GitHub")
    log.info("━" * 60)
    public_url = upload_image_to_github(image_path)
    log.info(f"Public URL: {public_url}")
    return public_url


def step_publish(public_url: str, caption: str) -> str:
    log.info("━" * 60)
    log.info("STEP 5 — Publishing to Instagram")
    log.info("━" * 60)
    post_id = publish_to_instagram(public_url, caption)
    log.info(f"Post ID: {post_id}")
    return post_id


# ── Main entry point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Current Affairs → Instagram Auto-Poster"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run everything except the final Instagram publish step",
    )
    parser.add_argument(
        "--test-image",
        action="store_true",
        help="Generate image from sample data only (no API calls at all)",
    )
    args = parser.parse_args()

    start = datetime.now(timezone.utc)
    log.info("=" * 60)
    log.info("  Current Affairs Instagram Auto-Poster")
    log.info(f"  {start.strftime('%d %B %Y  %H:%M UTC')}")
    log.info("=" * 60)

    try:
        if args.test_image:
            # ── Test mode: no external API calls ──────────────────────────
            log.info("Running in --test-image mode (sample data, no API calls)")
            sample = SAMPLE_POST_DATA.copy()
            sample["date"] = datetime.now(timezone.utc).strftime("%d %B %Y")
            sample["instagram_caption"] = sample["instagram_caption"].format(
                date=sample["date"]
            )
            image_path = step_generate_image(sample)
            log.info(f"\n✅ Test image created → {image_path}")
            log.info("Open the 'output/' folder to preview your image template.")
            return

        # ── Full pipeline ─────────────────────────────────────────────────
        news      = step_collect()
        if not news:
            log.warning("No fresh news articles found today. Exiting.")
            sys.exit(0)

        post_data  = step_summarize(news)
        
        # Step 2.5: Fact Check
        log.info("━" * 60)
        log.info("STEP 2.5 — Agentic Fact Checking")
        log.info("━" * 60)
        post_data = verify_post_data(post_data)
        
        image_path = step_generate_image(post_data)

        caption = post_data.get("caption") or post_data.get("instagram_caption", "Daily Current Affairs")
        if args.dry_run:
            log.info("\n✅ Dry run complete — image saved locally, NOT published.")
            log.info(f"   Image path: {image_path}")
            log.info("   Caption preview:\n")
            log.info(caption)
            return

        public_url = step_upload(image_path)
        post_id    = step_publish(public_url, caption)

        elapsed = (datetime.now(timezone.utc) - start).seconds
        log.info("=" * 60)
        log.info(f"  ✅ Pipeline complete in {elapsed}s")
        log.info(f"  Instagram Post ID: {post_id}")
        log.info("=" * 60)

    except Exception as e:
        log.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
