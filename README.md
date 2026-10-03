# 📰 Current Affairs Insta — Daily Auto-Poster

A fully automated, ₹0-cost pipeline that collects daily current affairs,
generates a branded Instagram post image, and publishes it every morning
using **GitHub Actions** — no paid server, no Canva, no paid API required.

---

## Architecture

```
RSS Feeds / NewsAPI
        ↓
  news_collector.py   ← fetch + deduplicate (SQLite)
        ↓
   summarizer.py      ← Groq LLM → structured JSON
        ↓
 image_generator.py   ← Pillow → 1080×1080 branded image
        ↓
    uploader.py       ← commit to GitHub → public raw URL
        ↓
   publisher.py       ← Meta Graph API → Instagram post
        ↓
      📱 Instagram
        ↑
  GitHub Actions      ← cron 7:00 AM IST every day
```

---

## Project Structure

```
Current Affairs Insta/
├── .github/workflows/daily_post.yml   # GitHub Actions scheduler
├── src/
│   ├── main.py                        # Pipeline orchestrator
│   ├── news_collector.py              # RSS + NewsAPI fetcher
│   ├── summarizer.py                  # Groq LLM summarizer
│   ├── image_generator.py             # Pillow image creator
│   ├── uploader.py                    # GitHub image uploader
│   └── publisher.py                   # Meta Graph API poster
├── config/
│   └── rss_feeds.json                 # RSS feed list (enable/disable)
├── assets/fonts/                      # NotoSans fonts (auto-downloaded in CI)
├── data/                              # SQLite DB (tracks posted articles)
├── output/                            # Generated images (local only)
├── requirements.txt
├── .env.example                       # Copy → .env and fill in secrets
└── README.md
```

---

## Quick Start (Local)

### 1 — Clone and set up

```bash
git clone https://github.com/YOUR_USERNAME/current-affairs-insta.git
cd "Current Affairs Insta"

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2 — Download fonts

```bash
mkdir -p assets/fonts
# Download NotoSans Bold and Regular into assets/fonts/
# Or run: python scripts/download_fonts.py
```

### 3 — Configure secrets

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

Required keys in `.env`:

| Key | Where to get it |
|-----|----------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) (free) |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Meta Graph API Explorer |
| `INSTAGRAM_ACCESS_TOKEN` | Meta Developer Dashboard (long-lived token) |
| `GITHUB_TOKEN` | GitHub → Settings → Developer Settings → Tokens (repo scope) |
| `GITHUB_IMAGE_REPO` | `yourusername/current-affairs-images` (must be public) |
| `INSTAGRAM_HANDLE` | e.g. `@currentaffairsdaily` |
| `NEWSAPI_KEY` | [newsapi.org](https://newsapi.org) (optional, free tier) |

### 4 — Test locally (no API calls)

```bash
# Generate a sample image from dummy data — no API keys needed
python src/main.py --test-image

# Check output/ folder for the generated image
```

### 5 — Dry run (fetches real news, skips Instagram publish)

```bash
python src/main.py --dry-run
```

### 6 — Full run

```bash
python src/main.py
```

---

## GitHub Actions Setup (Automated Daily Posting)

### Step 1 — Push this repo to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/current-affairs-insta.git
git push -u origin main
```

### Step 2 — Create a public image-hosting repo

Create a **new public repo** on GitHub named `current-affairs-images`.
This is where generated images are hosted for Instagram's API.

### Step 3 — Add GitHub Actions Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Your IG Business Account ID |
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived Instagram access token |
| `GH_IMAGE_TOKEN` | GitHub PAT with `repo` scope |
| `GITHUB_IMAGE_REPO` | `yourusername/current-affairs-images` |
| `INSTAGRAM_HANDLE` | `@yourhandle` |
| `NEWSAPI_KEY` | NewsAPI key (optional) |

### Step 4 — Enable Actions

Go to **Actions** tab → enable workflows if prompted.

The workflow runs automatically at **7:00 AM IST** every day.

To trigger manually: **Actions** → **Daily Current Affairs Post** → **Run workflow**.

---

## Customising RSS Feeds

Edit [`config/rss_feeds.json`](config/rss_feeds.json) to add, remove or
disable feeds:

```json
{
  "name": "My Feed",
  "url": "https://example.com/feed.rss",
  "category": "India",
  "enabled": true
}
```

Categories: `India`, `World`, `Economy`, `Science & Tech`, `Sports`

---

## Post Format

**Image (1080×1080 px):**
```
┌────────────────────────────────────┐
│  📰 DAILY CURRENT AFFAIRS          │
│     19 September 2026              │
├────────────────────────────────────┤
│ 🇮🇳 INDIA                          │
│  Headline goes here...             │
│  • Key point 1                     │
│  • Key point 2                     │
├────────────────────────────────────┤
│ 💰 ECONOMY                         │
│  RBI holds repo rate at 6.5%       │
│  • Repo rate unchanged             │
│  • GDP forecast: 7.2%             │
├────────────────────────────────────┤
│     @your_instagram_handle         │
└────────────────────────────────────┘
```

---

## Cost Summary

| Component | Cost |
|---|---|
| Instagram Professional account | ₹0 |
| Meta Developer App + Graph API | ₹0 |
| Groq API (free tier) | ₹0 |
| RSS Feeds | ₹0 |
| Python + Pillow | ₹0 |
| GitHub Repo + Actions | ₹0 |
| Image hosting (GitHub raw URL) | ₹0 |
| **Total** | **₹0** |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `GROQ_API_KEY not set` | Copy `.env.example` → `.env` and add your key |
| Instagram API 400 error | Check your access token hasn't expired (renew every ~60 days) |
| Image not found by Instagram | Ensure `GITHUB_IMAGE_REPO` is **public** |
| No news articles found | RSS feeds may be temporarily down; check `config/rss_feeds.json` |
| Font not found warning | Run the workflow once — fonts are auto-downloaded in CI |

---

## License

MIT — free to use, modify, and distribute.
