---
name: video-insights
description: >
  Watch and study videos end-to-end: search YouTube for a query, download
  videos, extract frame screenshots (the "images" of the video), fetch
  transcripts, then summarize findings with timestamped citations and visual
  evidence. Use when the user says things like "watch this video", "get
  screenshots from the video", "search for videos about X and summarize",
  "what does this video show", "grab frames + transcript", or pastes a
  youtube.com / youtu.be link and wants visuals, a transcript, or a summary.
---

# Video Insights

One CLI does all fetching: `scripts/vid.py`. It prints JSON to stdout, needs
no API key, and caches downloads in `~/.cache/video-insights/`. You do the
watching and analysis: the script fetches data and frames; you read the frames
as images, read the transcript, and write the findings.

## Setup (first use in a session)

```bash
python3 -c "import yt_dlp, youtube_transcript_api, imageio_ffmpeg" 2>/dev/null \
  || pip install -r scripts/requirements.txt
python3 scripts/vid.py doctor
```

`doctor` verifies deps, ffmpeg, and — critically — whether YouTube is
reachable through this environment's network policy. **Always run it first in
a new session.** If it reports blocked hosts, tell the user exactly what it
says: on Claude Code web they must edit the environment's network access to
allow `youtube.com`, `*.youtube.com`, `*.ytimg.com`, `*.googlevideo.com`
(docs: https://code.claude.com/docs/en/claude-code-on-the-web). Never try to
route around the policy. Local-file frame extraction works even when YouTube
is blocked.

ffmpeg is not required on the system — the `imageio-ffmpeg` pip package
bundles a static binary, which is what makes this skill work on restricted
environments without `apt`.

## Commands

Run from this skill's directory (or use the absolute path to `vid.py`).

```bash
python3 scripts/vid.py doctor
python3 scripts/vid.py search "QUERY" [--limit 10] [--sort relevance|date] [--max-duration MIN]
python3 scripts/vid.py info URL_OR_ID
python3 scripts/vid.py transcript URL_OR_ID [--lang en] [--format json|text] [--output FILE]
python3 scripts/vid.py download URL_OR_ID [--height 480] [--outdir DIR]
python3 scripts/vid.py frames SOURCE [--every 30 | --times 90,3:15 | --num 12 | --at-chapters] [--width 1280] [--outdir DIR]
python3 scripts/vid.py study URL_OR_ID [--every 60] [--num N] [--lang en] [--outdir DIR]
```

`frames SOURCE` accepts a YouTube URL/id **or a local video file** — the
latter needs no network at all.

## Core workflow: "watch" a video and report findings

When the user gives a video (or you found one via search):

1. **`study URL`** — one shot: downloads the video (480p, enough for
   screenshots), fetches metadata + chapters + transcript, and extracts
   frames (per-chapter when chapters exist, otherwise ~1 per minute, max 60).
   Everything lands in a bundle dir with a `manifest.json`.
2. **Look at the frames** with the Read tool — they are images; actually read
   the ones that matter rather than trusting filenames.
3. **Read the transcript** (`transcript.json` in the bundle; each segment has
   a `start` time in seconds). For long transcripts read selectively — never
   dump the whole thing into the conversation.
4. **Targeted re-capture**: when the transcript points at a key moment
   ("here's the diagram", "as you can see"), grab exact frames:
   `frames URL --times 4:32,12:05` — the video is already cached, so this
   is instant.
5. **Summarize findings** in Markdown:
   - every claim carries a timestamped link `https://youtu.be/<id>?t=<seconds>`
     (integer seconds), e.g. *"He shows the architecture at
     [4:32](https://youtu.be/abc123def45?t=272)"*;
   - reference the matching screenshots by file path (and send them with
     SendUserFile when the user should see them);
   - structure around chapters when they exist.

## Search-driven research

For "find videos about X and summarize what they say/show":

1. `search "X" --limit 10` with filters matching intent (`--sort date` for
   news, `--max-duration 30` to skip multi-hour streams).
2. Shortlist 2–4 candidates by title, views, recency. Don't study everything.
3. `study` each shortlisted video (or `transcript` first if you only need to
   check relevance cheaply — a transcript is much faster than a download).
4. Synthesize across videos: where sources agree/disagree, each claim cited
   with video + timestamp, screenshots as evidence.

## Frame-selection guide

| Situation | Flags |
| --- | --- |
| Overview of an unknown video | default `study` (chapters or ~1/min) |
| Slide-heavy talk or tutorial | `--every 30` |
| Specific moments from transcript | `--times 1:30,4:32,12:05` |
| Quick thumbnail-level scan | `--num 6` |
| Chaptered video | `--at-chapters` |

## Output conventions

- Default deliverable: a **Markdown report** — findings in prose, timestamped
  links, screenshot references. Tables only for comparisons.
- Frames are JPEGs named `frame_MM-SS.jpg` / `frame_HH-MM-SS.jpg` in the
  bundle's `frames/` dir.
- The user wants the raw data? Point them at the bundle dir; `--output` /
  `--outdir` flags redirect anything.

## Failure playbook

- Every `{"error": ...}` comes with a `hint` — follow it.
- **403 / proxy / tunnel errors** → network policy blocks YouTube. Run
  `doctor`, report its hint to the user verbatim, and stop; do not retry or
  work around. Frames on local files still work.
- **No transcript** → `info` shows `subtitles_available`; try another
  `--lang`, else fall back to description + chapters, and lean harder on
  frames (read more of them).
- **Extraction errors mid-session** (YouTube changes internals often) →
  `pip install -U yt-dlp`, retry once.
- **Age-restricted / private / region-locked** → report to the user; never
  attempt to bypass.
- **Huge videos**: `study` caps at 60 frames and downloads at 480p. For
  multi-hour videos prefer `transcript` first, then `frames --times` on the
  moments that matter.
