"""
Auto Pipeline - Fully Autonomous Content Engine
==================================================
Runs the entire content pipeline on autopilot:
  1. Generate content idea & script
  2. Download free stock footage (Pexels/Pixabay)
  3. Assemble vertical Short video (FFmpeg)
  4. Generate optimized caption & hashtags
  5. Upload to YouTube Shorts
  6. Upload to TikTok
  7. Wait and repeat on schedule

Usage:
    python auto_pipeline.py                  # Run once
    python auto_pipeline.py --loop           # Run continuously on schedule
    python auto_pipeline.py --loop --every 60  # Every 60 minutes
    python auto_pipeline.py --count 5        # Generate 5 videos then stop
"""

import os
import sys
import time
import random
import json
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from idea_generator import IdeaGenerator
from video_assembler import VideoAssembler
from caption_optimizer import CaptionOptimizer
from youtube_uploader import YouTubeUploader
from footage_downloader import FootageDownloader

try:
    from tiktok_uploader import TikTokUploader
    HAS_TIKTOK = True
except ImportError:
    HAS_TIKTOK = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def _log(msg, style="cyan"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if HAS_RICH:
        console.print(f"  [{style}][{timestamp}][/] {msg}")
    else:
        print(f"  [{timestamp}] {msg}")


def _log_step(step: int, total: int, msg: str):
    if HAS_RICH:
        console.print(f"\n  [bold magenta]━━━ Step {step}/{total}: {msg} ━━━[/]\n")
    else:
        print(f"\n  === Step {step}/{total}: {msg} ===\n")


class AutoPipeline:
    """
    Fully autonomous content generation and upload pipeline.
    Runs without any user input once configured.
    """

    def __init__(self):
        Config.ensure_dirs()
        self.idea_gen = IdeaGenerator()
        self.video_assembler = VideoAssembler()
        self.caption_opt = CaptionOptimizer()
        self.footage_dl = FootageDownloader()
        self.yt_uploader = YouTubeUploader()
        self.tiktok_uploader = TikTokUploader() if HAS_TIKTOK else None

        self.videos_created = 0
        self.videos_uploaded_yt = 0
        self.videos_uploaded_tt = 0
        self.run_log = []

    def run_once(self) -> dict:
        """
        Run the full pipeline once:
        Idea -> Download -> Assemble -> Caption -> Upload (YT + TikTok)

        Returns:
            Dict with results of the run
        """
        run_start = time.time()
        result = {
            "started_at": datetime.now().isoformat(),
            "idea": None,
            "video_path": None,
            "caption": None,
            "youtube_url": None,
            "tiktok_url": None,
            "success": False,
            "error": None,
        }

        if HAS_RICH:
            console.print(Panel(
                "[bold white]AUTONOMOUS PIPELINE[/]\n"
                "[dim]Idea -> Download -> Assemble -> Caption -> Upload[/]",
                border_style="magenta",
                title=f"[bold]Run #{self.videos_created + 1}[/]",
            ))

        try:
            # Step 1: Generate Idea
            _log_step(1, 6, "Generating Content Idea")
            idea = self.idea_gen.generate_script()
            hook = idea.get("hook", "Satisfying mini build")
            topic = idea.get("title", "house").split()[0].lower() if idea.get("title") else "house"
            _log(f"Hook: {hook[:60]}...")
            _log(f"Topic: {topic}")
            result["idea"] = idea

            # Step 2: Download Footage
            _log_step(2, 6, "Downloading FREE Stock Footage")
            clips = self.video_assembler.get_footage_clips()

            if len(clips) < 3:
                _log("Need more footage, downloading...")
                search_queries = [
                    f"miniature {topic}",
                    "construction timelapse",
                    "cement craft satisfying",
                    "bricklaying close up",
                    "mini building",
                ]
                query = random.choice(search_queries)
                downloaded = self.footage_dl.download_clips(query, count=5)
                _log(f"Downloaded {len(downloaded)} new clips", "green")
                clips = self.video_assembler.get_footage_clips()

            if not clips:
                _log("No footage available. Skipping video assembly.", "yellow")
                result["error"] = "No footage clips available"
                return result

            _log(f"Available clips: {len(clips)}", "green")

            # Step 3: Assemble Video
            _log_step(3, 6, "Assembling Vertical Short Video")
            video_path = self.video_assembler.assemble(
                hook=hook,
                max_duration=random.randint(30, 55),
            )

            if not video_path:
                _log("Video assembly failed!", "red")
                result["error"] = "Video assembly failed"
                return result

            result["video_path"] = video_path
            self.videos_created += 1
            _log(f"Video created: {os.path.basename(video_path)}", "green")

            # Step 4: Generate Caption
            _log_step(4, 6, "Generating Optimized Caption")
            caption_data = self.caption_opt.generate_full_caption(topic)
            title = caption_data.get("title", f"Mini {topic.title()} Build #Shorts")
            caption = caption_data.get("caption", "")
            tags = caption_data.get("hashtags", [])
            _log(f"Title: {title}")
            _log(f"Hashtags: {len(tags)}")
            result["caption"] = caption_data

            # Step 5: Upload to YouTube
            _log_step(5, 6, "Uploading to YouTube Shorts")
            try:
                if self.yt_uploader.authenticate():
                    yt_result = self.yt_uploader.upload_as_short(
                        video_path=video_path,
                        title=title,
                        description=caption,
                        tags=tags,
                    )
                    if yt_result:
                        result["youtube_url"] = yt_result.get("url")
                        self.videos_uploaded_yt += 1
                        _log(f"YouTube: {yt_result.get('url')}", "green")
                    else:
                        _log("YouTube upload failed", "yellow")
                else:
                    _log("YouTube not authenticated (skipping)", "yellow")
            except Exception as e:
                _log(f"YouTube error: {e}", "yellow")

            # Step 6: Upload to TikTok
            _log_step(6, 6, "Uploading to TikTok")
            try:
                if self.tiktok_uploader:
                    tt_result = self.tiktok_uploader.upload(
                        video_path=video_path,
                        caption=caption,
                    )
                    if tt_result:
                        result["tiktok_url"] = tt_result.get("url", "uploaded")
                        self.videos_uploaded_tt += 1
                        _log("TikTok: Upload successful!", "green")
                    else:
                        _log("TikTok upload failed", "yellow")
                else:
                    _log("TikTok uploader not available (skipping)", "yellow")
            except Exception as e:
                _log(f"TikTok error: {e}", "yellow")

            result["success"] = True

        except Exception as e:
            _log(f"Pipeline error: {e}", "red")
            result["error"] = str(e)

        # Summary
        duration = time.time() - run_start
        result["duration_seconds"] = round(duration, 1)
        self.run_log.append(result)

        if HAS_RICH:
            status = "[green]SUCCESS[/]" if result["success"] else "[red]FAILED[/]"
            console.print(Panel(
                f"Status: {status}\n"
                f"Video: {os.path.basename(result.get('video_path', 'N/A') or 'N/A')}\n"
                f"YouTube: {result.get('youtube_url', 'skipped')}\n"
                f"TikTok: {result.get('tiktok_url', 'skipped')}\n"
                f"Duration: {duration:.0f}s",
                border_style="green" if result["success"] else "red",
                title=f"[bold]Run #{self.videos_created} Complete[/]",
            ))

        return result

    def run_loop(self, interval_minutes: int = 60, max_runs: int = None):
        """
        Run the pipeline continuously on a schedule.

        Args:
            interval_minutes: Minutes between runs
            max_runs: Maximum number of runs (None = infinite)
        """
        _log(f"Starting autopilot mode: every {interval_minutes} minutes", "green")
        if max_runs:
            _log(f"Will stop after {max_runs} videos", "green")

        run_count = 0
        while True:
            run_count += 1
            _log(f"\n{'='*50}")
            _log(f"AUTOPILOT RUN #{run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            _log(f"{'='*50}\n")

            self.run_once()

            if max_runs and run_count >= max_runs:
                _log(f"Reached {max_runs} videos. Stopping.", "green")
                break

            # Wait for next run
            next_run = datetime.now() + timedelta(minutes=interval_minutes)
            _log(f"Next run at: {next_run.strftime('%H:%M')}")
            _log(f"Sleeping {interval_minutes} minutes...\n")

            try:
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                _log("Stopped by user.", "yellow")
                break

        self._show_summary()
        self._save_log()

    def _show_summary(self):
        """Show run summary."""
        if HAS_RICH:
            table = Table(box=box.DOUBLE_EDGE, border_style="cyan")
            table.add_column("Metric", style="bold")
            table.add_column("Value", style="white", justify="right")

            table.add_row("Videos Created", str(self.videos_created))
            table.add_row("YouTube Uploads", str(self.videos_uploaded_yt))
            table.add_row("TikTok Uploads", str(self.videos_uploaded_tt))
            table.add_row("Total Runs", str(len(self.run_log)))
            successful = sum(1 for r in self.run_log if r.get("success"))
            table.add_row("Successful", str(successful))
            table.add_row("Failed", str(len(self.run_log) - successful))

            console.print(Panel(table, title="[bold cyan]Autopilot Summary[/]", border_style="cyan"))
        else:
            print(f"\n  Summary: {self.videos_created} created, "
                  f"{self.videos_uploaded_yt} YT, {self.videos_uploaded_tt} TT")

    def _save_log(self):
        """Save run log to JSON."""
        log_path = os.path.join(Config.OUTPUT_DIR, "autopilot_log.json")
        with open(log_path, "w") as f:
            json.dump(self.run_log, f, indent=2, default=str)
        _log(f"Log saved: {log_path}")


# ═══════════════════════════════════════════════════════════
# Standalone entry point
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Content Pipeline")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--every", type=int, default=60, help="Minutes between runs (default: 60)")
    parser.add_argument("--count", type=int, default=None, help="Max videos to create")
    args = parser.parse_args()

    pipeline = AutoPipeline()

    if args.loop:
        pipeline.run_loop(interval_minutes=args.every, max_runs=args.count)
    elif args.count:
        pipeline.run_loop(interval_minutes=1, max_runs=args.count)
    else:
        pipeline.run_once()
