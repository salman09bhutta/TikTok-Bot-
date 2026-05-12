"""
Free Stock Footage Downloader
================================
Downloads construction/building clips from FREE stock video sources
(Pexels, Pixabay) for use in the Mini Building Construction content engine.

Free API Keys:
- Pexels: https://www.pexels.com/api/ (free, unlimited)
- Pixabay: https://pixabay.com/api/docs/ (free, 500 req/hour)

Usage:
    from footage_downloader import FootageDownloader
    fd = FootageDownloader()
    fd.download_clips("mini construction", count=10)
"""

import os
import sys
import json
import time
import random
import requests
from datetime import datetime
from config import Config

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def _log(msg):
    if HAS_RICH:
        console.print(f"  [green][FOOTAGE][/] {msg}")
    else:
        print(f"  [FOOTAGE] {msg}")


# ═══════════════════════════════════════════════════════════
# Search queries optimized for Mini Building Construction
# ═══════════════════════════════════════════════════════════

SEARCH_QUERIES = [
    "miniature construction",
    "mini building",
    "cement mixing",
    "bricklaying timelapse",
    "construction timelapse",
    "building house timelapse",
    "concrete pouring",
    "small house construction",
    "DIY cement craft",
    "woodworking small",
    "architecture model",
    "miniature house",
    "tiny house build",
    "construction worker hands",
    "laying bricks",
    "cement craft satisfying",
    "building foundation",
    "tiling floor",
    "plastering wall",
    "construction tools",
    "sand and cement",
    "mini pool construction",
    "model building",
    "scale model house",
    "carpentry close up",
]


class FootageDownloader:
    """Downloads free stock footage for mini building construction content."""

    def __init__(self):
        Config.ensure_dirs()
        self.pexels_key = os.getenv("PEXELS_API_KEY", Config.PEXELS_API_KEY if hasattr(Config, 'PEXELS_API_KEY') else "")
        self.pixabay_key = os.getenv("PIXABAY_API_KEY", Config.PIXABAY_API_KEY if hasattr(Config, 'PIXABAY_API_KEY') else "")
        self.downloaded = 0
        self.download_log = []

    def _get_pexels_videos(self, query: str, count: int = 5, orientation: str = "portrait") -> list:
        """
        Search Pexels for free videos.

        Args:
            query: Search term
            count: Number of results
            orientation: "portrait" (vertical), "landscape", or "square"

        Returns:
            List of video dicts with download URLs
        """
        if not self.pexels_key:
            return []

        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_key}
        params = {
            "query": query,
            "per_page": min(count, 80),
            "orientation": orientation,
            "size": "medium",
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            videos = []
            for video in data.get("videos", []):
                # Get the best quality file under 1080p
                video_files = video.get("video_files", [])
                best_file = None
                for vf in video_files:
                    if vf.get("height", 0) <= 1920 and vf.get("width", 0) <= 1080:
                        if best_file is None or vf.get("height", 0) > best_file.get("height", 0):
                            best_file = vf

                if not best_file and video_files:
                    best_file = video_files[0]

                if best_file:
                    videos.append({
                        "id": video["id"],
                        "url": best_file.get("link", ""),
                        "width": best_file.get("width", 0),
                        "height": best_file.get("height", 0),
                        "duration": video.get("duration", 0),
                        "source": "pexels",
                        "query": query,
                        "photographer": video.get("user", {}).get("name", "Unknown"),
                    })

            return videos

        except Exception as e:
            _log(f"[yellow]Pexels search failed: {e}[/]")
            return []

    def _get_pixabay_videos(self, query: str, count: int = 5) -> list:
        """
        Search Pixabay for free videos.

        Args:
            query: Search term
            count: Number of results

        Returns:
            List of video dicts with download URLs
        """
        if not self.pixabay_key:
            return []

        url = "https://pixabay.com/api/videos/"
        params = {
            "key": self.pixabay_key,
            "q": query,
            "per_page": min(count, 200),
            "video_type": "all",
            "safesearch": "true",
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            videos = []
            for hit in data.get("hits", []):
                video_data = hit.get("videos", {})
                # Prefer "medium" quality (720p-1080p)
                medium = video_data.get("medium", video_data.get("small", {}))

                if medium and medium.get("url"):
                    videos.append({
                        "id": hit["id"],
                        "url": medium["url"],
                        "width": medium.get("width", 0),
                        "height": medium.get("height", 0),
                        "duration": hit.get("duration", 0),
                        "source": "pixabay",
                        "query": query,
                        "photographer": hit.get("user", "Unknown"),
                    })

            return videos

        except Exception as e:
            _log(f"[yellow]Pixabay search failed: {e}[/]")
            return []

    def search_clips(self, query: str = None, count: int = 10) -> list:
        """
        Search all sources for video clips.

        Args:
            query: Search term (random construction query if None)
            count: Total clips to find

        Returns:
            Combined list of video results from all sources
        """
        if not query:
            query = random.choice(SEARCH_QUERIES)

        _log(f"Searching for: '{query}'...")

        all_videos = []

        # Search Pexels
        if self.pexels_key:
            pexels_results = self._get_pexels_videos(query, count=count)
            all_videos.extend(pexels_results)
            _log(f"  Pexels: {len(pexels_results)} clips found")

        # Search Pixabay
        if self.pixabay_key:
            pixabay_results = self._get_pixabay_videos(query, count=count)
            all_videos.extend(pixabay_results)
            _log(f"  Pixabay: {len(pixabay_results)} clips found")

        # If no API keys, show instructions
        if not self.pexels_key and not self.pixabay_key:
            _log("[yellow]No API keys configured![/]")
            _log("[yellow]Get FREE keys from:[/]")
            _log("[yellow]  Pexels: https://www.pexels.com/api/[/]")
            _log("[yellow]  Pixabay: https://pixabay.com/api/docs/[/]")
            _log("[yellow]Add to content_engine/.env:[/]")
            _log("[yellow]  PEXELS_API_KEY=your-key-here[/]")
            _log("[yellow]  PIXABAY_API_KEY=your-key-here[/]")
            return []

        _log(f"Total: {len(all_videos)} clips available")
        return all_videos[:count]

    def download_clip(self, video: dict, output_dir: str = None) -> str:
        """
        Download a single video clip.

        Args:
            video: Video dict from search results
            output_dir: Directory to save to (default: footage dir)

        Returns:
            Path to downloaded file, or None if failed
        """
        output_dir = output_dir or Config.FOOTAGE_DIR
        os.makedirs(output_dir, exist_ok=True)

        url = video.get("url", "")
        if not url:
            return None

        # Generate filename
        source = video.get("source", "unknown")
        vid_id = video.get("id", "unknown")
        query_safe = video.get("query", "clip").replace(" ", "_")[:20]
        filename = f"{source}_{query_safe}_{vid_id}.mp4"
        filepath = os.path.join(output_dir, filename)

        # Skip if already downloaded
        if os.path.exists(filepath):
            _log(f"Already have: {filename}")
            return filepath

        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with open(filepath, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)

            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            _log(f"Downloaded: {filename} ({file_size_mb:.1f} MB)")

            self.downloaded += 1
            self.download_log.append({
                "file": filepath,
                "source": source,
                "query": video.get("query"),
                "photographer": video.get("photographer"),
                "duration": video.get("duration"),
                "downloaded_at": datetime.now().isoformat(),
            })

            return filepath

        except Exception as e:
            _log(f"[red]Download failed: {e}[/]")
            # Clean up partial file
            if os.path.exists(filepath):
                os.remove(filepath)
            return None

    def download_clips(self, query: str = None, count: int = 5) -> list:
        """
        Search and download multiple clips.

        Args:
            query: Search term (random if None)
            count: Number of clips to download

        Returns:
            List of downloaded file paths
        """
        videos = self.search_clips(query, count=count * 2)  # Get extra in case some fail

        if not videos:
            return []

        downloaded_paths = []
        _log(f"Downloading {min(count, len(videos))} clips...")

        for video in videos[:count]:
            filepath = self.download_clip(video)
            if filepath:
                downloaded_paths.append(filepath)
            time.sleep(0.5)  # Rate limiting

        _log(f"[green]Downloaded {len(downloaded_paths)} clips to: {Config.FOOTAGE_DIR}[/]")
        return downloaded_paths

    def download_batch(self, queries: list = None, clips_per_query: int = 3) -> list:
        """
        Download clips from multiple search queries.

        Args:
            queries: List of search terms (uses built-in if None)
            clips_per_query: Clips to download per query

        Returns:
            All downloaded file paths
        """
        if not queries:
            queries = random.sample(SEARCH_QUERIES, min(5, len(SEARCH_QUERIES)))

        all_paths = []
        _log(f"Batch download: {len(queries)} queries × {clips_per_query} clips each")
        _log("")

        for i, query in enumerate(queries, 1):
            _log(f"[{i}/{len(queries)}] Query: '{query}'")
            paths = self.download_clips(query, count=clips_per_query)
            all_paths.extend(paths)
            time.sleep(1)  # Rate limiting between queries

        _log(f"\n[green]Batch complete! {len(all_paths)} total clips downloaded.[/]")
        return all_paths

    def get_existing_clips(self) -> list:
        """List already downloaded footage clips."""
        clips = []
        if os.path.exists(Config.FOOTAGE_DIR):
            for f in sorted(os.listdir(Config.FOOTAGE_DIR)):
                if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
                    filepath = os.path.join(Config.FOOTAGE_DIR, f)
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    clips.append({"file": filepath, "name": f, "size_mb": size_mb})
        return clips

    def display_status(self):
        """Display downloader status and existing clips."""
        existing = self.get_existing_clips()

        if HAS_RICH:
            table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
            table.add_column("Key", style="bold cyan")
            table.add_column("Value")

            table.add_row("Pexels API", "[green]Connected[/]" if self.pexels_key else "[red]No key[/]")
            table.add_row("Pixabay API", "[green]Connected[/]" if self.pixabay_key else "[red]No key[/]")
            table.add_row("Footage Dir", Config.FOOTAGE_DIR)
            table.add_row("Clips Downloaded", str(len(existing)))

            total_size = sum(c["size_mb"] for c in existing)
            table.add_row("Total Size", f"{total_size:.1f} MB")

            console.print(Panel(table, title="[bold green]Footage Downloader[/]", border_style="green"))

            if existing:
                clip_table = Table(box=box.ROUNDED, border_style="dim", show_lines=False)
                clip_table.add_column("#", style="bold", width=4)
                clip_table.add_column("Filename", style="white")
                clip_table.add_column("Size", style="cyan", justify="right")

                for i, clip in enumerate(existing[:10], 1):
                    clip_table.add_row(str(i), clip["name"][:50], f"{clip['size_mb']:.1f} MB")

                if len(existing) > 10:
                    clip_table.add_row("...", f"+{len(existing) - 10} more", "")

                console.print(clip_table)
        else:
            print(f"  Pexels: {'Connected' if self.pexels_key else 'No key'}")
            print(f"  Pixabay: {'Connected' if self.pixabay_key else 'No key'}")
            print(f"  Clips: {len(existing)}")
            print(f"  Dir: {Config.FOOTAGE_DIR}")

    def save_log(self):
        """Save download log to JSON."""
        if self.download_log:
            log_path = os.path.join(Config.OUTPUT_DIR, "download_log.json")
            with open(log_path, "w") as f:
                json.dump(self.download_log, f, indent=2)
            _log(f"Log saved: {log_path}")


# ═══════════════════════════════════════════════════════════
# Standalone usage
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    fd = FootageDownloader()

    print("\n  Stock Footage Downloader - Mini Building Construction")
    print("  " + "=" * 55)

    fd.display_status()

    if not fd.pexels_key and not fd.pixabay_key:
        print("\n  To get started:")
        print("  1. Get FREE Pexels API key: https://www.pexels.com/api/")
        print("  2. Get FREE Pixabay API key: https://pixabay.com/api/docs/")
        print("  3. Add to content_engine/.env:")
        print("     PEXELS_API_KEY=your-key")
        print("     PIXABAY_API_KEY=your-key")
        print("  4. Run again!")
    else:
        print("\n  Downloading construction footage...")
        paths = fd.download_batch(clips_per_query=2)
        fd.save_log()
        print(f"\n  Done! {len(paths)} clips ready in: {Config.FOOTAGE_DIR}")
