"""
Free Music Downloader
========================
Downloads royalty-free background music from Pixabay Music API
for use in Mini Building Construction Shorts.

All music from Pixabay is FREE for commercial use (no attribution required).

Usage:
    python download_music.py              # Download 10 tracks
    python download_music.py --count 20   # Download 20 tracks
"""

import os
import sys
import time
import random
import argparse
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def _log(msg):
    if HAS_RICH:
        console.print(f"  [green][MUSIC][/] {msg}")
    else:
        print(f"  [MUSIC] {msg}")


# Search queries for construction/satisfying background music
MUSIC_QUERIES = [
    "lofi chill",
    "satisfying background",
    "construction ambient",
    "upbeat positive",
    "motivational beat",
    "cinematic short",
    "ambient relaxing",
    "electronic chill",
    "piano calm",
    "inspiring background",
    "happy upbeat",
    "corporate positive",
    "timelapse music",
    "energetic beat",
    "soft acoustic",
]


def download_pixabay_music(api_key: str, query: str, count: int = 3) -> list:
    """Download music tracks from Pixabay."""
    if not api_key:
        return []

    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "media_type": "music",
        "per_page": min(count * 2, 200),
        "safesearch": "true",
        "order": "popular",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        downloaded = []
        for hit in data.get("hits", [])[:count]:
            audio_url = hit.get("previewURL") or hit.get("largeImageURL", "").replace("_640", "")

            if not audio_url:
                continue

            # Generate filename
            title = hit.get("tags", "track").split(",")[0].strip().replace(" ", "_")[:30]
            track_id = hit.get("id", random.randint(1000, 9999))
            filename = f"pixabay_{title}_{track_id}.mp3"
            filepath = os.path.join(Config.MUSIC_DIR, filename)

            if os.path.exists(filepath):
                _log(f"Already have: {filename}")
                downloaded.append(filepath)
                continue

            try:
                resp = requests.get(audio_url, stream=True, timeout=30)
                resp.raise_for_status()

                with open(filepath, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)

                size_kb = os.path.getsize(filepath) / 1024
                _log(f"Downloaded: {filename} ({size_kb:.0f} KB)")
                downloaded.append(filepath)
            except Exception as e:
                _log(f"[yellow]Failed: {filename} ({e})[/]")

            time.sleep(0.5)

        return downloaded

    except Exception as e:
        _log(f"[yellow]Pixabay music search failed: {e}[/]")
        return []


def download_free_music_samples() -> list:
    """Download a few free sample tracks that don't need an API key."""
    Config.ensure_dirs()
    downloaded = []

    # Free music URLs (public domain / CC0)
    free_tracks = [
        {
            "name": "lofi_chill_beat.mp3",
            "url": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
        },
        {
            "name": "upbeat_construction.mp3",
            "url": "https://cdn.pixabay.com/download/audio/2022/10/25/audio_946bc498e4.mp3",
        },
        {
            "name": "satisfying_ambient.mp3",
            "url": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
        },
    ]

    _log("Downloading sample music tracks (free, no API key needed)...")

    for track in free_tracks:
        filepath = os.path.join(Config.MUSIC_DIR, track["name"])
        if os.path.exists(filepath):
            _log(f"Already have: {track['name']}")
            downloaded.append(filepath)
            continue

        try:
            resp = requests.get(track["url"], stream=True, timeout=30)
            if resp.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                size_kb = os.path.getsize(filepath) / 1024
                _log(f"Downloaded: {track['name']} ({size_kb:.0f} KB)")
                downloaded.append(filepath)
            else:
                _log(f"[yellow]Skipped: {track['name']} (HTTP {resp.status_code})[/]")
        except Exception as e:
            _log(f"[yellow]Failed: {track['name']} ({e})[/]")

        time.sleep(1)

    return downloaded


def main():
    parser = argparse.ArgumentParser(description="Download free background music")
    parser.add_argument("--count", type=int, default=10, help="Tracks to download")
    args = parser.parse_args()

    Config.ensure_dirs()

    if HAS_RICH:
        console.print(Panel(
            "[bold white]Free Music Downloader[/]\n"
            "[dim]Royalty-free tracks for Mini Building Shorts[/]",
            border_style="green",
        ))
    else:
        print("\n  Free Music Downloader for Content Engine\n")

    # Check for Pixabay API key
    pixabay_key = os.getenv("PIXABAY_API_KEY", Config.PIXABAY_API_KEY if hasattr(Config, "PIXABAY_API_KEY") else "")

    all_downloaded = []

    if pixabay_key:
        _log(f"Using Pixabay API (searching {args.count} tracks)...")
        queries = random.sample(MUSIC_QUERIES, min(5, len(MUSIC_QUERIES)))

        for query in queries:
            _log(f"Searching: '{query}'")
            tracks = download_pixabay_music(pixabay_key, query, count=args.count // 5 + 1)
            all_downloaded.extend(tracks)
            time.sleep(1)

            if len(all_downloaded) >= args.count:
                break
    else:
        _log("[yellow]No Pixabay API key. Downloading sample tracks...[/]")
        _log("[yellow]For more music, add PIXABAY_API_KEY to .env[/]")
        all_downloaded = download_free_music_samples()

    # Summary
    existing = [f for f in os.listdir(Config.MUSIC_DIR)
                if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))] if os.path.exists(Config.MUSIC_DIR) else []

    if HAS_RICH:
        console.print(f"\n  [green]Done! {len(all_downloaded)} new tracks downloaded.[/]")
        console.print(f"  [green]Total music library: {len(existing)} tracks[/]")
        console.print(f"  [dim]Location: {Config.MUSIC_DIR}[/]\n")
    else:
        print(f"\n  Done! {len(all_downloaded)} new, {len(existing)} total tracks")
        print(f"  Location: {Config.MUSIC_DIR}\n")


if __name__ == "__main__":
    main()
