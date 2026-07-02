#!/usr/bin/env python3
"""YouTube scraper CLI: search, video metadata, transcripts, channels,
playlists, comments, trending, related videos, batch mode.

All commands print JSON to stdout (or CSV with --format csv). Failures print
{"error": ..., "hint": ...} to stdout and exit non-zero. No API key needed.
"""

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

CACHE_DIR = Path(os.environ.get("YT_SCRAPER_CACHE", Path.home() / ".cache" / "youtube-scraper"))
DAY = 86400
# TTL per subcommand; None = cache forever
CACHE_TTL = {
    "video": None,
    "transcript": None,
    "search": DAY,
    "channel": DAY,
    "playlist": DAY,
    "comments": DAY,
    "trending": 6 * 3600,
    "related": DAY,
}

UPDATE_HINT = "If extraction keeps failing, YouTube may have changed internals: pip install -U yt-dlp"


def fail(error, hint=None):
    out = {"error": str(error)}
    if hint:
        out["hint"] = hint
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(1)


# ---------------------------------------------------------------- id parsing

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(s):
    """Accept bare IDs, watch/shorts/live/embed URLs, and youtu.be links."""
    s = s.strip()
    if VIDEO_ID_RE.match(s):
        return s
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/live/|/embed/)([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)
    fail(f"Could not extract a video ID from: {s}",
         "Pass a full YouTube URL or an 11-character video ID")


def channel_url(s):
    """Accept @handle, UC... id, plain handle, or any channel URL."""
    s = s.strip().rstrip("/")
    if s.startswith(("http://", "https://")):
        # strip a trailing tab so we can append our own
        s = re.sub(r"/(videos|shorts|streams|playlists|featured|about|community)$", "", s)
        return s
    if re.match(r"^UC[A-Za-z0-9_-]{22}$", s):
        return f"https://www.youtube.com/channel/{s}"
    if not s.startswith("@"):
        s = "@" + s
    return f"https://www.youtube.com/{s}"


def playlist_url(s):
    s = s.strip()
    if s.startswith(("http://", "https://")):
        return s
    return f"https://www.youtube.com/playlist?list={s}"


# ------------------------------------------------------------------- caching

def cache_key(command, args_dict):
    payload = json.dumps([command, args_dict], sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()


def cache_get(command, args_dict, no_cache=False, refresh=False):
    if no_cache or refresh:
        return None
    path = CACHE_DIR / f"{cache_key(command, args_dict)}.json"
    if not path.exists():
        return None
    try:
        entry = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    ttl = CACHE_TTL.get(command)
    if ttl is not None and time.time() - entry.get("cached_at", 0) > ttl:
        return None
    return entry.get("data")


def cache_put(command, args_dict, data, no_cache=False):
    if no_cache:
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = CACHE_DIR / f"{cache_key(command, args_dict)}.json"
        path.write_text(json.dumps({"cached_at": time.time(), "data": data}, ensure_ascii=False))
    except OSError:
        pass  # caching is best-effort


# -------------------------------------------------------------------- output

def flatten_row(d):
    row = {}
    for k, v in d.items():
        if isinstance(v, (dict, list)):
            row[k] = json.dumps(v, ensure_ascii=False)
        else:
            row[k] = v
    return row


def emit(result, fmt="json", output=None):
    if fmt == "csv":
        # CSV needs rows: use the entries/segments/comments list if the result
        # is a wrapper dict, else wrap a single object.
        rows = result
        if isinstance(result, dict):
            for key in ("entries", "videos", "segments", "comments", "related", "results"):
                if isinstance(result.get(key), list):
                    rows = result[key]
                    break
            else:
                rows = [result]
        rows = [flatten_row(r) for r in rows if isinstance(r, dict)]
        if not rows:
            fail("Nothing to export as CSV", "The result contained no rows; try --format json")
        fields = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        text = buf.getvalue()
    else:
        text = json.dumps(result, ensure_ascii=False, indent=2)

    if output:
        Path(output).write_text(text)
        print(json.dumps({"written": output,
                          "items": len(result.get("entries", []) or []) if isinstance(result, dict) else len(result)}))
    else:
        print(text)


# -------------------------------------------------------------------- yt-dlp

def ydl_extract(url, flat=False, extra_opts=None, playlist_end=None):
    import yt_dlp
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "ignoreerrors": False,
        "extract_flat": "in_playlist" if flat else False,
    }
    if playlist_end:
        opts["playlistend"] = playlist_end
    if extra_opts:
        opts.update(extra_opts)
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def trim_entry(e):
    """Normalize a flat playlist/search entry to a compact schema."""
    if not isinstance(e, dict):
        return None
    kind = "video"
    ie_key = (e.get("ie_key") or "").lower()
    url = e.get("url") or e.get("webpage_url") or ""
    if "playlist" in ie_key or "list=" in url and "watch" not in url:
        kind = "playlist"
    if ie_key in ("youtubetab",) and ("/channel/" in url or "/@" in url):
        kind = "channel"
    vid = e.get("id")
    out = {
        "id": vid,
        "type": kind,
        "title": e.get("title"),
        "url": e.get("webpage_url") or url or (f"https://www.youtube.com/watch?v={vid}" if kind == "video" and vid else None),
        "channel": e.get("channel") or e.get("uploader"),
        "channel_id": e.get("channel_id"),
        "duration": e.get("duration"),
        "view_count": e.get("view_count"),
        "live_status": e.get("live_status"),
    }
    if e.get("timestamp"):
        out["upload_date"] = datetime.fromtimestamp(e["timestamp"], tz=timezone.utc).strftime("%Y%m%d")
    elif e.get("upload_date"):
        out["upload_date"] = e["upload_date"]
    return out


def trim_video(info):
    fields = [
        "id", "title", "description", "channel", "channel_id", "channel_url",
        "channel_follower_count", "uploader", "upload_date", "timestamp",
        "duration", "duration_string", "view_count", "like_count",
        "comment_count", "tags", "categories", "chapters", "webpage_url",
        "live_status", "was_live", "availability", "age_limit", "language",
    ]
    out = {k: info.get(k) for k in fields if info.get(k) is not None}
    vid = info.get("id")
    if vid:
        out["short_url"] = f"https://youtu.be/{vid}"
    thumbs = info.get("thumbnails") or []
    if thumbs:
        best = max(thumbs, key=lambda t: (t.get("width") or 0))
        out["thumbnail"] = best.get("url")
    subs = info.get("subtitles") or {}
    autos = info.get("automatic_captions") or {}
    out["has_manual_subtitles"] = sorted(subs.keys())[:20]
    out["has_auto_captions"] = bool(autos)
    return out


# ------------------------------------------------------- search filter (sp=)

def _varint(n):
    out = b""
    while True:
        b7 = n & 0x7F
        n >>= 7
        if n:
            out += bytes([b7 | 0x80])
        else:
            out += bytes([b7])
            return out


def _field(num, value):
    return _varint((num << 3) | 0) + _varint(value)


SORT_CODES = {"relevance": 0, "rating": 1, "date": 2, "views": 3}
DATE_CODES = {"hour": 1, "today": 2, "week": 3, "month": 4, "year": 5}
TYPE_CODES = {"video": 1, "channel": 2, "playlist": 3, "movie": 4}
DURATION_CODES = {"short": 1, "long": 2, "medium": 3}
FEATURE_FIELDS = {"hd": 4, "subtitles": 5, "creativecommons": 6, "3d": 7,
                  "live": 8, "4k": 14, "360": 15, "hdr": 25, "vr180": 26}


def build_sp(sort=None, upload_date=None, result_type=None, duration=None, features=None):
    """Encode YouTube's native search-filter protobuf into the sp= URL param."""
    filters = b""
    if upload_date:
        filters += _field(1, DATE_CODES[upload_date])
    if result_type:
        filters += _field(2, TYPE_CODES[result_type])
    if duration:
        filters += _field(3, DURATION_CODES[duration])
    for f in features or []:
        filters += _field(FEATURE_FIELDS[f], 1)
    msg = b""
    if sort:
        msg += _field(1, SORT_CODES[sort])
    if filters:
        msg += _varint((2 << 3) | 2) + _varint(len(filters)) + filters
    if not msg:
        return None
    return base64.urlsafe_b64encode(msg).decode().rstrip("=")


def parse_date(date_str, flag):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        fail(f"Invalid date for {flag}: {date_str!r}", "Use YYYY-MM-DD, e.g. --after 2026-01-01")


def date_to_bucket(date_str):
    """Map an --after date onto YouTube's native upload-date buckets."""
    dt = parse_date(date_str, "--after")
    age = datetime.now(timezone.utc) - dt
    if age <= timedelta(hours=1):
        return "hour"
    if age <= timedelta(days=1):
        return "today"
    if age <= timedelta(days=7):
        return "week"
    if age <= timedelta(days=31):
        return "month"
    if age <= timedelta(days=366):
        return "year"
    return None  # older than a year: no native bucket, no filtering needed


# ---------------------------------------------------------------- innertube

def innertube_next(video_id):
    """Fetch the watch-page 'next' payload (source of related videos)."""
    import requests
    resp = requests.post(
        "https://www.youtube.com/youtubei/v1/next",
        json={
            "context": {"client": {"clientName": "WEB", "clientVersion": "2.20250101.00.00"}},
            "videoId": video_id,
        },
        headers={"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _runs_text(node):
    if not isinstance(node, dict):
        return None
    if "simpleText" in node:
        return node["simpleText"]
    if "runs" in node:
        return "".join(r.get("text", "") for r in node["runs"])
    if "content" in node and isinstance(node["content"], str):
        return node["content"]
    return None


def parse_related(payload, limit):
    """Walk the response tree for known related-video renderers (both the
    legacy compactVideoRenderer and the newer lockupViewModel shapes)."""
    found, seen = [], set()

    def visit(node):
        if len(found) >= limit:
            return
        if isinstance(node, dict):
            if "compactVideoRenderer" in node:
                r = node["compactVideoRenderer"]
                vid = r.get("videoId")
                if vid and vid not in seen:
                    seen.add(vid)
                    found.append({
                        "id": vid,
                        "title": _runs_text(r.get("title")),
                        "channel": _runs_text(r.get("longBylineText")),
                        "views": _runs_text(r.get("viewCountText")),
                        "length": _runs_text(r.get("lengthText")),
                        "url": f"https://www.youtube.com/watch?v={vid}",
                    })
            elif "lockupViewModel" in node:
                r = node["lockupViewModel"]
                vid = r.get("contentId")
                if vid and VIDEO_ID_RE.match(vid or "") and vid not in seen:
                    meta = r.get("metadata", {}).get("lockupMetadataViewModel", {})
                    title = _runs_text(meta.get("title")) or _runs_text(r.get("title"))
                    if title:
                        seen.add(vid)
                        found.append({
                            "id": vid,
                            "title": title,
                            "url": f"https://www.youtube.com/watch?v={vid}",
                        })
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for v in node:
                visit(v)

    secondary = (payload.get("contents", {})
                 .get("twoColumnWatchNextResults", {})
                 .get("secondaryResults", {}))
    visit(secondary if secondary else payload)
    return found


# ------------------------------------------------------------------ commands

def cmd_search(args):
    key = {"q": args.query, "limit": args.limit, "sort": args.sort,
           "after": args.after, "before": args.before, "duration": args.duration,
           "type": args.type, "features": sorted(args.features or [])}
    cached = cache_get("search", key, args.no_cache, args.refresh)
    if cached is not None:
        return cached

    upload_bucket = date_to_bucket(args.after) if args.after else None
    before_dt = parse_date(args.before, "--before").strftime("%Y%m%d") if args.before else None
    sp = build_sp(sort=None if args.sort == "relevance" else args.sort,
                  upload_date=upload_bucket, result_type=args.type,
                  duration=args.duration, features=args.features)
    from urllib.parse import quote_plus
    url = f"https://www.youtube.com/results?search_query={quote_plus(args.query)}"
    if sp:
        url += f"&sp={sp}"

    fetch_n = args.limit * 3 if args.before else args.limit
    info = ydl_extract(url, flat=True, playlist_end=min(fetch_n, 100))
    entries = [t for t in (trim_entry(e) for e in info.get("entries") or []) if t]

    warnings = []
    if before_dt:
        # Flat search entries carry no upload date; fetch metadata per result
        # to filter precisely. Slow, so it is opt-in via --before.
        kept = []
        for e in entries:
            if e["type"] != "video":
                continue
            try:
                full = ydl_extract(f"https://www.youtube.com/watch?v={e['id']}")
                if full.get("upload_date") and full["upload_date"] <= before_dt:
                    e["upload_date"] = full["upload_date"]
                    kept.append(e)
            except Exception:
                continue
            if len(kept) >= args.limit:
                break
        entries = kept
        warnings.append("--before requires fetching each result's metadata; results limited to videos")

    result = {"query": args.query, "url": url, "count": len(entries[:args.limit]),
              "entries": entries[:args.limit]}
    if upload_bucket:
        warnings.append(f"--after mapped to YouTube's native '{upload_bucket}' upload-date bucket")
    if warnings:
        result["warnings"] = warnings
    cache_put("search", key, result, args.no_cache)
    return result


def cmd_video(args):
    vid = extract_video_id(args.video)
    key = {"id": vid, "related": bool(args.related)}
    cached = cache_get("video", key, args.no_cache, args.refresh)
    if cached is not None:
        return cached

    info = ydl_extract(f"https://www.youtube.com/watch?v={vid}")
    result = trim_video(info)

    if args.related:
        try:
            result["related"] = parse_related(innertube_next(vid), limit=20)
            if not result["related"]:
                result["related_warning"] = "No related videos parsed; YouTube may have changed the response shape"
        except Exception as exc:
            result["related"] = []
            result["related_warning"] = f"Related lookup failed: {exc}"

    if result.get("live_status") in ("is_live", "is_upcoming"):
        return result  # do not cache in-flight live data
    cache_put("video", key, result, args.no_cache)
    return result


def cmd_transcript(args):
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

    vid = extract_video_id(args.video)
    api = YouTubeTranscriptApi()

    if args.list_langs:
        try:
            tl = api.list(vid)
        except (TranscriptsDisabled, VideoUnavailable) as exc:
            fail(exc, "This video has no transcripts; fall back to `video` (description) and `comments`")
        langs = [{"language": t.language, "code": t.language_code,
                  "auto_generated": t.is_generated,
                  "translatable": t.is_translatable} for t in tl]
        return {"video_id": vid, "available_transcripts": langs}

    key = {"id": vid, "lang": args.lang, "translate": args.translate}
    cached = cache_get("transcript", key, args.no_cache, args.refresh)
    if cached is None:
        try:
            if args.translate:
                tl = api.list(vid)
                transcript = tl.find_transcript(args.lang.split(",") if args.lang else ["en"])
                fetched = transcript.translate(args.translate).fetch()
            else:
                langs = args.lang.split(",") if args.lang else ["en"]
                fetched = api.fetch(vid, languages=langs)
        except (TranscriptsDisabled, VideoUnavailable) as exc:
            fail(exc, "No transcript available; fall back to `video` (description) and `comments`")
        except NoTranscriptFound as exc:
            fail(exc, f"No transcript in requested language; run `transcript {vid} --list-langs` to see options")
        segments = [{"start": round(s.start, 2), "duration": round(s.duration, 2), "text": s.text}
                    for s in fetched]
        cached = {"video_id": vid, "language": fetched.language_code,
                  "auto_generated": fetched.is_generated, "segments": segments}
        cache_put("transcript", key, cached, args.no_cache)

    if args.format == "text":
        return {"video_id": cached["video_id"], "language": cached["language"],
                "text": " ".join(s["text"] for s in cached["segments"])}
    if args.format == "srt":
        def ts(sec):
            ms = int(round(sec * 1000))
            h, rem = divmod(ms, 3600000)
            m, rem = divmod(rem, 60000)
            s, ms = divmod(rem, 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"
        lines = []
        for i, seg in enumerate(cached["segments"], 1):
            lines.append(f"{i}\n{ts(seg['start'])} --> {ts(seg['start'] + seg['duration'])}\n{seg['text']}\n")
        return {"video_id": cached["video_id"], "srt": "\n".join(lines)}
    return cached


def cmd_channel(args):
    base = channel_url(args.channel)
    key = {"url": base, "tab": args.tab, "limit": args.limit}
    cached = cache_get("channel", key, args.no_cache, args.refresh)
    if cached is not None:
        return cached

    info = ydl_extract(f"{base}/{args.tab}", flat=True, playlist_end=args.limit)
    entries = [t for t in (trim_entry(e) for e in info.get("entries") or []) if t]
    result = {
        "channel": info.get("channel") or info.get("uploader"),
        "channel_id": info.get("channel_id"),
        "channel_url": info.get("channel_url") or base,
        "subscriber_count": info.get("channel_follower_count"),
        "description": info.get("description"),
        "tags": info.get("tags"),
        "tab": args.tab,
        "count": len(entries),
        "entries": entries,
    }
    cache_put("channel", key, result, args.no_cache)
    return result


def cmd_playlist(args):
    url = playlist_url(args.playlist)
    key = {"url": url, "limit": args.limit}
    cached = cache_get("playlist", key, args.no_cache, args.refresh)
    if cached is not None:
        return cached

    info = ydl_extract(url, flat=True, playlist_end=args.limit)
    entries = [t for t in (trim_entry(e) for e in info.get("entries") or []) if t]
    result = {
        "playlist_id": info.get("id"),
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "description": info.get("description"),
        "count": len(entries),
        "entries": entries,
    }
    cache_put("playlist", key, result, args.no_cache)
    return result


def cmd_comments(args):
    vid = extract_video_id(args.video)
    key = {"id": vid, "limit": args.limit, "sort": args.sort, "replies": not args.no_replies}
    cached = cache_get("comments", key, args.no_cache, args.refresh)
    if cached is not None:
        return cached

    max_replies = "0" if args.no_replies else "all"
    info = ydl_extract(
        f"https://www.youtube.com/watch?v={vid}",
        extra_opts={
            "getcomments": True,
            "extractor_args": {"youtube": {
                # max-comments, max-parents, max-replies, max-replies-per-thread
                "max_comments": [str(args.limit), "all", max_replies, "10"],
                "comment_sort": [args.sort],
            }},
        },
    )
    comments = []
    for c in (info.get("comments") or [])[:args.limit]:
        comments.append({
            "id": c.get("id"),
            "author": c.get("author"),
            "text": c.get("text"),
            "like_count": c.get("like_count"),
            "timestamp": c.get("timestamp"),
            "parent": c.get("parent"),
            "is_reply": c.get("parent") not in (None, "root"),
            "author_is_uploader": c.get("author_is_uploader"),
            "is_pinned": c.get("is_pinned"),
        })
    result = {"video_id": vid, "title": info.get("title"),
              "comment_count_total": info.get("comment_count"),
              "sort": args.sort, "count": len(comments), "comments": comments}
    cache_put("comments", key, result, args.no_cache)
    return result


def cmd_trending(args):
    key = {"region": args.region}
    cached = cache_get("trending", key, args.no_cache, args.refresh)
    if cached is not None:
        return cached

    url = "https://www.youtube.com/feed/trending"
    if args.region:
        url += f"?gl={args.region.upper()}"
    try:
        info = ydl_extract(url, flat=True, playlist_end=args.limit)
    except Exception as exc:
        fail(exc, "YouTube retired the Trending page in 2025 in some regions. "
                  "Fallback: `search <topic> --sort views --after <last week's date>`")
    entries = [t for t in (trim_entry(e) for e in info.get("entries") or []) if t]
    if not entries:
        fail("Trending feed returned no entries",
             "YouTube retired the Trending page in 2025 in some regions. "
             "Fallback: `search <topic> --sort views --after <last week's date>`")
    result = {"region": args.region or "default", "count": len(entries), "entries": entries}
    cache_put("trending", key, result, args.no_cache)
    return result


def cmd_batch(args, parser):
    try:
        raw = Path(args.file).read_text()
    except OSError as exc:
        fail(f"Cannot read batch file: {exc}", "Pass --file with one URL/ID/query per line")
    lines = [ln.strip() for ln in raw.splitlines()
             if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        fail(f"No inputs found in {args.file}", "One URL/ID/query per line; # starts a comment")

    import contextlib
    results = []
    for i, line in enumerate(lines):
        if i > 0:
            time.sleep(random.uniform(0.5, 1.5))  # politeness between items
        sub_argv = [args.subcommand, line] + args.rest
        # handlers report failures via fail(), which prints JSON and exits;
        # capture that stdout so it becomes the per-item error instead of
        # corrupting the batch JSON document
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                sub_args = parser.parse_args(sub_argv)
                data = sub_args.handler(sub_args)
            results.append({"input": line, "ok": True, "result": data})
        except SystemExit:
            item = {"input": line, "ok": False}
            try:
                err = json.loads(buf.getvalue())
                item["error"] = err.get("error", buf.getvalue().strip())
                if err.get("hint"):
                    item["hint"] = err["hint"]
            except (json.JSONDecodeError, AttributeError):
                item["error"] = buf.getvalue().strip() or "subcommand failed (bad arguments)"
            results.append(item)
        except Exception as exc:
            results.append({"input": line, "ok": False, "error": str(exc)})
    ok = sum(1 for r in results if r["ok"])
    return {"batch": args.subcommand, "total": len(results), "succeeded": ok,
            "failed": len(results) - ok, "results": results}


# ---------------------------------------------------------------------- main

def add_common(p):
    p.add_argument("--format", choices=["json", "csv"], default="json",
                   help="output format (default: json)")
    p.add_argument("--output", metavar="FILE", help="write output to a file instead of stdout")
    p.add_argument("--no-cache", action="store_true", help="bypass the cache entirely")
    p.add_argument("--refresh", action="store_true", help="re-fetch and overwrite the cached copy")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="yt.py", description="Keyless YouTube scraper: JSON out, cached, no API key.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search", help="search YouTube with native filters")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--sort", choices=list(SORT_CODES), default="relevance")
    p.add_argument("--after", metavar="YYYY-MM-DD",
                   help="only results uploaded after this date (mapped to YouTube's hour/today/week/month/year buckets)")
    p.add_argument("--before", metavar="YYYY-MM-DD",
                   help="only results uploaded before this date (slow: fetches metadata per result)")
    p.add_argument("--duration", choices=list(DURATION_CODES),
                   help="short <4min, medium 4-20min, long >20min")
    p.add_argument("--type", choices=list(TYPE_CODES), help="restrict result type")
    p.add_argument("--features", nargs="+", choices=list(FEATURE_FIELDS),
                   help="require features, e.g. --features live subtitles hd")
    add_common(p)
    p.set_defaults(handler=cmd_search)

    p = sub.add_parser("video", help="full metadata for one video")
    p.add_argument("video", help="URL or 11-char video ID")
    p.add_argument("--related", action="store_true", help="also fetch related videos")
    add_common(p)
    p.set_defaults(handler=cmd_video)

    p = sub.add_parser("transcript", help="transcript with timestamps")
    p.add_argument("video", help="URL or 11-char video ID")
    p.add_argument("--lang", help="preferred language code(s), comma-separated (default: en)")
    p.add_argument("--translate", metavar="CODE", help="translate the transcript to this language")
    p.add_argument("--list-langs", action="store_true", help="list available transcript languages")
    p.add_argument("--format", choices=["json", "text", "srt", "csv"], default="json",
                   help="json = timestamped segments, text = plain text, srt = subtitles")
    p.add_argument("--output", metavar="FILE")
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--refresh", action="store_true")
    p.set_defaults(handler=cmd_transcript)

    p = sub.add_parser("channel", help="channel info + uploads/shorts/streams/playlists")
    p.add_argument("channel", help="@handle, channel URL, or UC... id")
    p.add_argument("--tab", choices=["videos", "shorts", "streams", "playlists"], default="videos")
    p.add_argument("--limit", type=int, default=30)
    add_common(p)
    p.set_defaults(handler=cmd_channel)

    p = sub.add_parser("playlist", help="all videos in a playlist")
    p.add_argument("playlist", help="playlist URL or ID")
    p.add_argument("--limit", type=int, default=200)
    add_common(p)
    p.set_defaults(handler=cmd_playlist)

    p = sub.add_parser("comments", help="comments and reply threads")
    p.add_argument("video", help="URL or 11-char video ID")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--sort", choices=["top", "new"], default="top")
    p.add_argument("--no-replies", action="store_true", help="top-level comments only")
    add_common(p)
    p.set_defaults(handler=cmd_comments)

    p = sub.add_parser("trending", help="trending videos (availability varies by region)")
    p.add_argument("--region", metavar="CC", help="ISO country code, e.g. US, JP, DE")
    p.add_argument("--limit", type=int, default=30)
    add_common(p)
    p.set_defaults(handler=cmd_trending)

    p = sub.add_parser("batch", help="run a subcommand over every line of a file; "
                                     "extra flags are passed through to the subcommand")
    p.add_argument("subcommand", choices=["search", "video", "transcript", "channel",
                                          "playlist", "comments"])
    p.add_argument("--file", required=True, help="one URL/ID/query per line, # for comments")
    p.add_argument("--output", metavar="FILE")
    p.set_defaults(handler=None, format="json")

    return parser


def main():
    parser = build_parser()
    # batch forwards unrecognized flags to its subcommand, so parse leniently
    args, extra = parser.parse_known_args()
    if args.command == "batch":
        args.rest = extra
    elif extra:
        parser.error(f"unrecognized arguments: {' '.join(extra)}")
    try:
        if args.command == "batch":
            result = cmd_batch(args, parser)
        else:
            result = args.handler(args)
        emit(result, fmt=getattr(args, "format", "json"), output=args.output)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        fail("Interrupted")
    except Exception as exc:
        name = type(exc).__name__
        msg = str(exc)
        hint = UPDATE_HINT
        low = msg.lower()
        if "proxy" in low or "tunnel" in low or "resolve" in low or "connection" in low:
            hint = "Network problem reaching YouTube; check connectivity/proxy policy for www.youtube.com"
        elif "sign in" in low or "age" in low:
            hint = "Video is age-restricted or requires login; report this rather than bypassing it"
        elif "private" in low or "unavailable" in low:
            hint = "Video is private, deleted, or region-locked"
        elif "429" in msg or "too many" in low:
            hint = "Rate-limited by YouTube; wait a few minutes and rely on cached data"
        fail(f"{name}: {msg}", hint)


if __name__ == "__main__":
    main()
