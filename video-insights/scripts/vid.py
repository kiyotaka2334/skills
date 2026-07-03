#!/usr/bin/env python3
"""video-insights CLI: search YouTube, download videos, grab frame screenshots,
fetch transcripts, and bundle everything for analysis.

Every command prints JSON to stdout. Errors print {"error": ..., "hint": ...}
and exit 1. No API keys required.
"""

import argparse
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path(os.environ.get("VIDEO_INSIGHTS_CACHE", Path.home() / ".cache" / "video-insights"))
YT_HOSTS = ["www.youtube.com", "i.ytimg.com", "redirector.googlevideo.com"]


def die(error, hint):
    print(json.dumps({"error": error, "hint": hint}, indent=2))
    sys.exit(1)


def out(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def ffmpeg_exe():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        die("ffmpeg not found",
            "Install the bundled binary with: pip install imageio-ffmpeg (no apt needed)")


def require_yt_dlp():
    try:
        import yt_dlp
        return yt_dlp
    except ImportError:
        die("yt-dlp not installed", "Run: pip install -r scripts/requirements.txt")


def video_id_of(url_or_id):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", url_or_id)
    if m:
        return m.group(1)
    if re.fullmatch(r"[\w-]{11}", url_or_id):
        return url_or_id
    return None


def canonical_url(url_or_id):
    vid = video_id_of(url_or_id)
    return f"https://www.youtube.com/watch?v={vid}" if vid else url_or_id


def parse_ts(ts):
    """'90', '1:30', or '01:02:03' -> seconds (float)."""
    parts = [float(p) for p in str(ts).split(":")]
    secs = 0.0
    for p in parts:
        secs = secs * 60 + p
    return secs


def fmt_ts(seconds):
    s = int(seconds)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}-{m:02d}-{s:02d}" if h else f"{m:02d}-{s:02d}"


def proxy_error_hint(exc_text):
    if "403" in exc_text and ("proxy" in exc_text.lower() or "tunnel" in exc_text.lower()):
        return ("This environment's network policy blocks YouTube. Run 'doctor' to confirm. "
                "On Claude Code web, edit the environment's network access to allow: "
                "youtube.com, *.youtube.com, *.ytimg.com, *.googlevideo.com — "
                "see https://code.claude.com/docs/en/claude-code-on-the-web")
    return "Transient failure — retry once; if it persists run: pip install -U yt-dlp"


# ---------------------------------------------------------------- commands

def cmd_doctor(args):
    report = {"python": sys.version.split()[0], "checks": {}}

    for mod in ("yt_dlp", "youtube_transcript_api", "imageio_ffmpeg"):
        try:
            __import__(mod)
            report["checks"][mod] = "ok"
        except ImportError:
            report["checks"][mod] = "MISSING - pip install -r scripts/requirements.txt"

    try:
        exe = shutil.which("ffmpeg")
        if not exe:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
        report["checks"]["ffmpeg"] = exe
    except Exception:
        report["checks"]["ffmpeg"] = "MISSING - pip install imageio-ffmpeg"

    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    report["proxy"] = proxy or "none"
    blocked = []
    for host in YT_HOSTS:
        report["checks"][host] = _probe(host, proxy)
        if report["checks"][host] != "reachable":
            blocked.append(host)

    report["youtube_reachable"] = not blocked
    if blocked:
        report["hint"] = (
            "YouTube hosts are blocked by the network policy. On Claude Code web, "
            "edit this environment's network access to allow youtube.com, *.youtube.com, "
            "*.ytimg.com and *.googlevideo.com (or use 'Unrestricted'). Docs: "
            "https://code.claude.com/docs/en/claude-code-on-the-web. "
            "Local frame extraction ('frames' on a file) still works without network.")
    out(report)
    sys.exit(0 if not blocked else 1)


def _probe(host, proxy, timeout=8):
    try:
        if proxy:
            m = re.match(r"https?://([^:/]+):(\d+)", proxy)
            with socket.create_connection((m.group(1), int(m.group(2))), timeout=timeout) as s:
                s.sendall(f"CONNECT {host}:443 HTTP/1.1\r\nHost: {host}:443\r\n\r\n".encode())
                status = s.recv(1024).decode(errors="replace").split("\r\n")[0]
            return "reachable" if " 200" in status else f"blocked ({status.strip()})"
        with socket.create_connection((host, 443), timeout=timeout) as raw:
            ssl.create_default_context().wrap_socket(raw, server_hostname=host).close()
        return "reachable"
    except Exception as e:
        return f"unreachable ({type(e).__name__}: {e})"


def _entry(e):
    return {
        "id": e.get("id"),
        "url": f"https://www.youtube.com/watch?v={e.get('id')}",
        "title": e.get("title"),
        "channel": e.get("channel") or e.get("uploader"),
        "duration_s": e.get("duration"),
        "view_count": e.get("view_count"),
        "upload_date": e.get("upload_date"),
    }


def cmd_search(args):
    yt_dlp = require_yt_dlp()
    prefix = "ytsearchdate" if args.sort == "date" else "ytsearch"
    opts = {"quiet": True, "no_warnings": True, "extract_flat": "in_playlist",
            "playlist_items": f"1:{args.limit}"}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"{prefix}{args.limit}:{args.query}", download=False)
    except Exception as e:
        die(f"search failed: {e}", proxy_error_hint(str(e)))
    results = [_entry(e) for e in info.get("entries", []) if e]
    if args.max_duration:
        results = [r for r in results
                   if r["duration_s"] and r["duration_s"] <= args.max_duration * 60]
    out({"query": args.query, "count": len(results), "results": results})


def _extract_info(url):
    yt_dlp = require_yt_dlp()
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            return ydl.extract_info(canonical_url(url), download=False)
    except Exception as e:
        die(f"metadata fetch failed: {e}", proxy_error_hint(str(e)))


def cmd_info(args):
    info = _extract_info(args.url)
    out({
        **_entry(info),
        "description": (info.get("description") or "")[:2000],
        "like_count": info.get("like_count"),
        "chapters": info.get("chapters") or [],
        "subtitles_available": sorted((info.get("subtitles") or {}).keys()),
        "auto_captions_available": bool(info.get("automatic_captions")),
    })


def cmd_transcript(args):
    vid = video_id_of(args.url)
    if not vid:
        die("could not parse a YouTube video id from input",
            "Pass a youtube.com/youtu.be URL or a bare 11-char video id.")
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        fetched = api.fetch(vid, languages=[args.lang, "en"])
        segments = [{"start": round(s.start, 2), "duration": round(s.duration, 2),
                     "text": s.text} for s in fetched]
    except Exception as e:
        die(f"transcript fetch failed: {e}",
            proxy_error_hint(str(e)) if "proxy" in str(e).lower() or "403" in str(e)
            else "Video may have no captions. Try 'info' to check subtitles_available, "
                 "or fall back to description/chapters/comments.")
    if args.format == "text":
        body = "\n".join(f"[{int(s['start'])}s] {s['text']}" for s in segments)
        result = {"video_id": vid, "format": "text", "transcript": body}
    else:
        result = {"video_id": vid, "segment_count": len(segments), "segments": segments}
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False)
                                     if args.format != "text" else result["transcript"])
        out({"written": args.output, "video_id": vid, "segment_count": len(segments)})
    else:
        out(result)


def _download(url, height, outdir):
    yt_dlp = require_yt_dlp()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    vid = video_id_of(url) or "video"
    existing = list(outdir.glob(f"{vid}.*"))
    if existing:
        return existing[0], True
    opts = {
        "quiet": True, "no_warnings": True,
        "format": f"best[height<={height}][ext=mp4]/best[height<={height}]/best",
        "outtmpl": str(outdir / f"{vid}.%(ext)s"),
        "ffmpeg_location": str(Path(ffmpeg_exe()).parent),
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(canonical_url(url), download=True)
    except Exception as e:
        die(f"download failed: {e}", proxy_error_hint(str(e)))
    files = list(outdir.glob(f"{vid}.*"))
    if not files:
        die("download produced no file", "Retry with --height 360, or pip install -U yt-dlp")
    return files[0], False


def cmd_download(args):
    path, cached = _download(args.url, args.height, args.outdir or CACHE_DIR / "videos")
    out({"file": str(path), "cached": cached,
         "size_mb": round(path.stat().st_size / 1e6, 1)})


def _resolve_source(url_or_file, height):
    """Local file path or URL -> (local video path, video_id or None)."""
    p = Path(url_or_file)
    if p.exists():
        return p, None
    vid = video_id_of(url_or_file)
    if not vid and not url_or_file.startswith("http"):
        die(f"'{url_or_file}' is neither an existing file nor a URL/video id",
            "Pass a local video file, a YouTube URL, or an 11-char video id.")
    path, _ = _download(url_or_file, height, CACHE_DIR / "videos")
    return path, vid


def _duration_of(video_path):
    exe = ffmpeg_exe()
    r = subprocess.run([exe, "-i", str(video_path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", r.stderr)
    if not m:
        die(f"could not read duration of {video_path}", "File may be corrupt; re-download.")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def _grab_frames(video_path, timestamps, outdir, width):
    exe = ffmpeg_exe()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    frames = []
    for t in timestamps:
        name = f"frame_{fmt_ts(t)}.jpg"
        dest = outdir / name
        cmd = [exe, "-y", "-loglevel", "error", "-ss", str(t), "-i", str(video_path),
               "-frames:v", "1", "-q:v", "2", "-vf", f"scale='min({width},iw)':-2",
               str(dest)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and dest.exists() and dest.stat().st_size > 0:
            frames.append({"time_s": round(t, 1), "timestamp": fmt_ts(t).replace("-", ":"),
                           "file": str(dest)})
        else:
            frames.append({"time_s": round(t, 1), "error": r.stderr.strip()[:200] or "empty frame"})
    return frames


def _plan_timestamps(args, duration, chapters):
    if args.times:
        return sorted(parse_ts(t) for t in args.times.split(","))
    if args.at_chapters:
        if not chapters:
            die("video has no chapters", "Use --every or --num instead.")
        return [c["start_time"] + 1 for c in chapters]
    if args.every:
        step = parse_ts(args.every)
        return [t for t in _frange(step / 2, duration, step)]
    n = args.num or 12
    step = duration / (n + 1)
    return [step * (i + 1) for i in range(n)]


def _frange(start, stop, step):
    t = start
    while t < stop:
        yield t
        t += step


def cmd_frames(args):
    path, vid = _resolve_source(args.source, args.height)
    duration = _duration_of(path)
    chapters = None
    if args.at_chapters and vid:
        chapters = _extract_info(args.source).get("chapters")
    ts = _plan_timestamps(args, duration, chapters)
    if len(ts) > 100:
        die(f"{len(ts)} frames requested (max 100)", "Increase --every or lower --num.")
    outdir = args.outdir or (CACHE_DIR / "frames" / (vid or path.stem))
    frames = _grab_frames(path, ts, outdir, args.width)
    out({"video": str(path), "duration_s": round(duration, 1),
         "frame_dir": str(outdir), "frames": frames})


def cmd_study(args):
    """One-shot: download + frames + transcript + metadata into a bundle dir."""
    vid = video_id_of(args.url)
    if not vid:
        die("study needs a YouTube URL or video id", "For local files use 'frames'.")
    bundle = Path(args.outdir or f"./video_study_{vid}")
    bundle.mkdir(parents=True, exist_ok=True)

    info = _extract_info(args.url)
    meta = {**_entry(info), "description": (info.get("description") or "")[:2000],
            "chapters": info.get("chapters") or []}
    (bundle / "info.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    path, _ = _download(args.url, args.height, CACHE_DIR / "videos")
    duration = _duration_of(path)

    transcript_file = None
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        fetched = YouTubeTranscriptApi().fetch(vid, languages=[args.lang, "en"])
        segs = [{"start": round(s.start, 2), "text": s.text} for s in fetched]
        transcript_file = bundle / "transcript.json"
        transcript_file.write_text(json.dumps(segs, indent=2, ensure_ascii=False))
    except Exception as e:
        (bundle / "transcript_error.txt").write_text(str(e))

    chapters = meta["chapters"]
    if chapters and not args.every and not args.num:
        ts = [c["start_time"] + 1 for c in chapters]
    else:
        n = args.num or min(16, max(6, int(duration // 60)))
        step = parse_ts(args.every) if args.every else duration / (n + 1)
        ts = list(_frange(step if args.every else step, duration, step))[:60]
    frames = _grab_frames(path, ts, bundle / "frames", args.width)

    manifest = {
        "video_id": vid, "title": meta["title"], "channel": meta["channel"],
        "duration_s": round(duration, 1), "url": meta["url"],
        "bundle_dir": str(bundle),
        "video_file": str(path),
        "info": str(bundle / "info.json"),
        "transcript": str(transcript_file) if transcript_file else None,
        "transcript_note": None if transcript_file else "unavailable - see transcript_error.txt",
        "frames": frames,
        "next_steps": "Read frames with the Read tool (they are images), read transcript.json, "
                      "then summarize with timestamped citations: https://youtu.be/"
                      f"{vid}?t=<seconds>",
    }
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    out(manifest)


def main():
    p = argparse.ArgumentParser(prog="vid.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="check environment readiness (deps, ffmpeg, network)")

    s = sub.add_parser("search", help="search YouTube")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--sort", choices=["relevance", "date"], default="relevance")
    s.add_argument("--max-duration", type=int, help="max video length in minutes")

    s = sub.add_parser("info", help="video metadata + chapters")
    s.add_argument("url")

    s = sub.add_parser("transcript", help="fetch transcript")
    s.add_argument("url")
    s.add_argument("--lang", default="en")
    s.add_argument("--format", choices=["json", "text"], default="json")
    s.add_argument("--output", help="write to file instead of stdout")

    s = sub.add_parser("download", help="download video")
    s.add_argument("url")
    s.add_argument("--height", type=int, default=480, help="max resolution (default 480)")
    s.add_argument("--outdir")

    s = sub.add_parser("frames", help="extract screenshot frames from URL or local file")
    s.add_argument("source", help="YouTube URL/id or local video file")
    s.add_argument("--every", help="one frame every N seconds (e.g. 30 or 1:00)")
    s.add_argument("--times", help="comma-separated timestamps (e.g. 90,3:15,10:00)")
    s.add_argument("--num", type=int, help="N evenly spaced frames (default 12)")
    s.add_argument("--at-chapters", action="store_true", help="one frame per chapter")
    s.add_argument("--width", type=int, default=1280)
    s.add_argument("--height", type=int, default=480, help="download resolution cap")
    s.add_argument("--outdir")

    s = sub.add_parser("study", help="one-shot bundle: info + video + transcript + frames")
    s.add_argument("url")
    s.add_argument("--every", help="frame interval (default: chapters or ~1/min, max 60)")
    s.add_argument("--num", type=int)
    s.add_argument("--lang", default="en")
    s.add_argument("--width", type=int, default=1280)
    s.add_argument("--height", type=int, default=480)
    s.add_argument("--outdir")

    args = p.parse_args()
    {"doctor": cmd_doctor, "search": cmd_search, "info": cmd_info,
     "transcript": cmd_transcript, "download": cmd_download,
     "frames": cmd_frames, "study": cmd_study}[args.cmd](args)


if __name__ == "__main__":
    main()
