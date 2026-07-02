---
name: youtube-scraper
description: >
  Research YouTube for any question or topic: search with filters, scrape video
  metadata, transcripts, comments, channels, playlists, related and trending
  videos — then answer questions with timestamped citations, summarize videos,
  and analyze channels. Use when the user says things like "search YouTube",
  "find videos about", "get the transcript", "summarize this video",
  "what does this channel post", "compare these channels", "scrape comments",
  or pastes a youtube.com / youtu.be link and asks anything about it.
---

# YouTube Scraper

All scraping goes through one CLI: `scripts/yt.py`. It needs no API key, prints
JSON to stdout, and caches results in `~/.cache/youtube-scraper/`. You do the
analysis; the script only fetches data.

## Setup (first use in a session)

```bash
python3 -c "import yt_dlp, youtube_transcript_api" 2>/dev/null || pip install -r scripts/requirements.txt
```

If extraction errors appear mid-session (YouTube changes internals regularly),
run `pip install -U yt-dlp` once and retry.

## Commands

Run every command from this skill's directory (or use the absolute path to `yt.py`).

```bash
python3 scripts/yt.py search "QUERY" --limit 10 --sort date --duration medium --after 2026-01-01 --features subtitles
python3 scripts/yt.py video URL_OR_ID [--related]
python3 scripts/yt.py transcript URL_OR_ID [--lang en] [--translate de] [--list-langs] [--format json|text|srt]
python3 scripts/yt.py channel @HANDLE [--tab videos|shorts|streams|playlists] [--limit 30]
python3 scripts/yt.py playlist URL_OR_ID
python3 scripts/yt.py comments URL_OR_ID [--limit 50] [--sort top|new] [--no-replies]
python3 scripts/yt.py trending [--region US]
python3 scripts/yt.py batch SUBCOMMAND --file inputs.txt [subcommand flags...]
```

Common flags: `--format csv`, `--output FILE`, `--no-cache`, `--refresh`.
Field-by-field output schemas and the full filter reference are in
`references/schemas.md` — read it when you need a field you don't see below.

## Core workflow: answering a question from YouTube

This is the main loop. When the user asks a question ("what does X say about Y",
"find the best explanation of Z"):

1. **Search** with filters that match the intent (`--sort date` for news-like
   questions, `--duration medium/long` for tutorials, `--after` for recency).
2. **Shortlist 3–5 candidates** from the results by title relevance, view
   count, and recency. Don't transcript everything.
3. **Fetch transcripts** for the shortlist. Long transcripts: write them to a
   file with `--output` and read selectively — never dump a full transcript
   into the conversation.
4. **Locate the answer segments** in the transcript (each segment has a
   `start` time in seconds).
5. **Answer with timestamped citations.** Every claim links to the exact
   moment: `https://youtu.be/<id>?t=<seconds>` (integer seconds). Example:
   *"He recommends X over Y ([12:34](https://youtu.be/abc123def45?t=754))"*.

If a video has no transcript, fall back in order: `--list-langs` (try another
language or `--translate`), then the video's `description` and `chapters`, then
top `comments`.

## Summarization

- **Single video**: transcript + `chapters` from `video`. Structure the summary
  around chapters when they exist; include timestamped links to key sections.
- **Topic across videos**: search → transcripts of the top 3–5 → synthesize.
  Note where sources agree and disagree, and cite each claim's video+timestamp.

## Channel analytics

Fetch `channel` (and `--tab shorts` / `--tab streams` for format mix). Compute
from the JSON yourself — no extra tooling:

- **Upload cadence**: spacing of `upload_date` across recent entries.
- **Engagement rate**: (like_count + comment_count) / view_count per video
  (needs `video` calls for likes/comments; `batch video --file ids.txt` helps).
- **Top videos**: sort entries by `view_count`.
- **Comparisons**: side-by-side Markdown table per channel — subscribers,
  cadence, median views, engagement, format mix.

## Output conventions

- Default deliverable: a **Markdown report** with clickable (timestamped where
  relevant) links. Tables for comparisons, prose for findings.
- When the user wants data files: `--format csv --output file.csv` or
  `--output file.json`. The script writes files; you don't re-serialize.

## Failure playbook

- `{"error": ...}` always comes with a `hint` — follow it.
- Extraction failures across the board → `pip install -U yt-dlp`, retry once.
- Age-restricted / private / region-locked → report it to the user; never
  attempt to bypass.
- Rate-limited (HTTP 429) → wait, and lean on the cache (`--refresh` only when
  freshness genuinely matters).
- `trending` may be empty (YouTube retired the page in some regions) → fall
  back to `search <topic> --sort views --after <a week ago>`.
- Batch runs report per-item `ok`/`error` and keep going; summarize failures at
  the end instead of aborting.
