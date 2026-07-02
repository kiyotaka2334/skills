# yt.py output schemas & reference

Everything is JSON on stdout. Errors: `{"error": "...", "hint": "..."}` + exit 1.
Numbers may be `null` when YouTube doesn't expose them (e.g. hidden like counts).

## search

```json
{
  "query": "...", "url": "https://www.youtube.com/results?...",
  "count": 10,
  "entries": [
    {
      "id": "dQw4w9WgXcQ", "type": "video|playlist|channel",
      "title": "...", "url": "https://www.youtube.com/watch?v=...",
      "channel": "...", "channel_id": "UC...",
      "duration": 212.0, "view_count": 123456,
      "live_status": null, "upload_date": "20260101"
    }
  ],
  "warnings": ["only present when filters were approximated"]
}
```

- `--after YYYY-MM-DD` maps to YouTube's native buckets (hour/today/week/month/
  year) — it is approximate, and dates older than a year apply no filter.
- `--before YYYY-MM-DD` is exact but slow (fetches metadata per result) and
  returns videos only.
- `--features` accepts: hd, subtitles, creativecommons, 3d, live, 4k, 360, hdr, vr180.
- Flat search entries usually have no `upload_date`; fetch `video` for it.

## video

```json
{
  "id": "...", "title": "...", "description": "...",
  "channel": "...", "channel_id": "UC...", "channel_url": "...",
  "channel_follower_count": 1000000,
  "upload_date": "20260101", "timestamp": 1767225600,
  "duration": 212, "duration_string": "3:32",
  "view_count": 1, "like_count": 1, "comment_count": 1,
  "tags": ["..."], "categories": ["..."],
  "chapters": [{"start_time": 0.0, "end_time": 60.0, "title": "Intro"}],
  "webpage_url": "...", "short_url": "https://youtu.be/...",
  "live_status": "not_live|is_live|was_live|is_upcoming", "was_live": false,
  "availability": "public", "age_limit": 0, "language": "en",
  "thumbnail": "https://...", 
  "has_manual_subtitles": ["en", "de"], "has_auto_captions": true,
  "related": [{"id": "...", "title": "...", "channel": "...", "views": "...", "url": "..."}]
}
```

`related` only with `--related`; it uses YouTube's internal `next` endpoint and
degrades to `[]` + `related_warning` if YouTube changes the response shape.

## transcript

```json
{
  "video_id": "...", "language": "en", "auto_generated": true,
  "segments": [{"start": 12.34, "duration": 3.2, "text": "..."}]
}
```

- `--format text` → `{"video_id", "language", "text"}` (one plain string).
- `--format srt` → `{"video_id", "srt"}`.
- `--list-langs` → `{"video_id", "available_transcripts": [{"language", "code", "auto_generated", "translatable"}]}`.
- Timestamped deep link: `https://youtu.be/<video_id>?t=<int(start)>`.

## channel

```json
{
  "channel": "...", "channel_id": "UC...", "channel_url": "...",
  "subscriber_count": 1000000, "description": "...", "tags": ["..."],
  "tab": "videos|shorts|streams|playlists",
  "count": 30, "entries": [ /* same shape as search entries */ ]
}
```

## playlist

```json
{"playlist_id": "PL...", "title": "...", "channel": "...",
 "description": "...", "count": 50, "entries": [ /* search-entry shape */ ]}
```

## comments

```json
{
  "video_id": "...", "title": "...", "comment_count_total": 5000,
  "sort": "top|new", "count": 50,
  "comments": [
    {"id": "...", "author": "@name", "text": "...", "like_count": 10,
     "timestamp": 1767225600, "parent": "root",
     "is_reply": false, "author_is_uploader": false, "is_pinned": false}
  ]
}
```

Replies have `parent` set to the parent comment id and `is_reply: true`.

## trending

```json
{"region": "US", "count": 30, "entries": [ /* search-entry shape */ ]}
```

## batch

```json
{"batch": "video", "total": 3, "succeeded": 2, "failed": 1,
 "results": [{"input": "...", "ok": true, "result": { /* subcommand output */ }},
             {"input": "...", "ok": false, "error": "..."}]}
```

Input file: one URL/ID/query per line, `#` starts a comment. Extra flags after
`--file X` are forwarded to the subcommand, e.g.
`batch transcript --file ids.txt --format text`.

## Caching

`~/.cache/youtube-scraper/` (override with `YT_SCRAPER_CACHE`). Transcripts and
video metadata cache forever; search/channel/playlist/comments 24h; trending 6h.
Live/upcoming videos are never cached. `--refresh` re-fetches one call;
`--no-cache` skips read *and* write. Clear it all: `rm -rf ~/.cache/youtube-scraper`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Every extraction fails / weird parse errors | `pip install -U yt-dlp` (YouTube changed internals) |
| "Sign in to confirm your age" | Age-restricted; report to user, don't bypass |
| Transcript errors | `transcript ID --list-langs`, try another code or `--translate en`; else use description + comments |
| HTTP 429 | Rate-limited: wait a few minutes, rely on cache |
| `trending` empty | Page retired in some regions → `search <topic> --sort views --after <last week>` |
| Proxy/tunnel/connection errors | Network policy blocks youtube.com (common in sandboxes) |

## Live smoke test

Run where youtube.com is reachable:

```bash
python3 scripts/yt.py search "python asyncio tutorial" --limit 5
python3 scripts/yt.py video dQw4w9WgXcQ --related
python3 scripts/yt.py transcript dQw4w9WgXcQ --format text
python3 scripts/yt.py channel @veritasium --limit 10
python3 scripts/yt.py playlist PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr
python3 scripts/yt.py comments dQw4w9WgXcQ --limit 20 --no-replies
python3 scripts/yt.py trending --region US
```
