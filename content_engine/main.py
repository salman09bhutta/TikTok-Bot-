"""
AI Content Engine - Main Entry Point
=======================================
Mini Building Construction niche content automation.

Modules:
  1. Content Idea Generator - AI scripts, hooks, concepts
  2. Video Assembler - FFmpeg/MoviePy vertical Shorts
  3. YouTube Shorts Uploader - Auto-upload & schedule
  4. Caption & Hashtag Optimizer - Viral captions & tags

Usage:
    python main.py          # Interactive menu
    python main.py --ideas  # Generate content ideas
    python main.py --video  # Assemble a video
    python main.py --upload # Upload to YouTube
    python main.py --caption # Generate captions
    python main.py --full   # Full pipeline (idea → video → caption → upload)
"""

import argparse
import sys
import os
import time
from datetime import datetime

# Ensure content_engine is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from idea_generator import IdeaGenerator
from video_assembler import VideoAssembler
from caption_optimizer import CaptionOptimizer
from youtube_uploader import YouTubeUploader
from footage_downloader import FootageDownloader

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from rich import box
    from pyfiglet import Figlet
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def show_banner():
    """Display the content engine banner."""
    if HAS_RICH:
        try:
            fig = Figlet(font="small")
            ascii_art = fig.renderText("Content Engine")
            console.print(f"[bold cyan]{ascii_art}[/]")
        except Exception:
            console.print("[bold cyan]  AI Content Engine[/]\n")

        console.print(Panel(
            "[bold white]Mini Building Construction[/] — Niche Content Automation\n"
            "[dim]Ideas → Videos → Captions → Upload → Growth[/]",
            border_style="magenta",
            title="[bold]v1.0[/]",
            subtitle="[dim]TikTok & YouTube Shorts[/]",
        ))
    else:
        print("""
  ╔══════════════════════════════════════════════════════╗
  ║    AI Content Engine - Mini Building Construction    ║
  ║    Ideas → Videos → Captions → Upload → Growth      ║
  ╚══════════════════════════════════════════════════════╝
        """)


def show_status():
    """Display system status."""
    Config.ensure_dirs()
    warnings = Config.validate()

    va = VideoAssembler()
    clips = va.get_footage_clips()
    tracks = va.get_music_tracks()

    if HAS_RICH:
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Component", style="bold")
        table.add_column("Status")

        # AI
        ai_status = "[green]Ready[/]" if (Config.OPENAI_API_KEY or Config.GEMINI_API_KEY) else "[yellow]No API key (templates only)[/]"
        table.add_row("AI Engine", ai_status)

        # Video
        ffmpeg_status = "[green]Ready[/]" if va.has_ffmpeg else "[red]Not installed[/]"
        table.add_row("FFmpeg", ffmpeg_status)
        table.add_row("MoviePy", "[green]Ready[/]" if va.has_moviepy else "[yellow]Not installed[/]")
        table.add_row("Footage Clips", f"[white]{len(clips)} files[/]")
        table.add_row("Music Tracks", f"[white]{len(tracks)} files[/]")

        # YouTube
        yt_status = "[green]Token found[/]" if os.path.exists("token.json") else "[yellow]Not authenticated[/]"
        table.add_row("YouTube API", yt_status)

        # Dirs
        table.add_row("Output Dir", f"[dim]{Config.OUTPUT_DIR}[/]")
        table.add_row("Footage Dir", f"[dim]{Config.FOOTAGE_DIR}[/]")

        console.print(Panel(table, title="[bold cyan]System Status[/]", border_style="cyan"))

        if warnings:
            for w in warnings:
                console.print(f"  [yellow]⚠ {w}[/]")
            console.print()
    else:
        print(f"  AI: {'Ready' if (Config.OPENAI_API_KEY or Config.GEMINI_API_KEY) else 'Templates only'}")
        print(f"  FFmpeg: {'Ready' if va.has_ffmpeg else 'Missing'}")
        print(f"  Clips: {len(clips)} | Music: {len(tracks)}")
        print(f"  YouTube: {'Authenticated' if os.path.exists('token.json') else 'Not connected'}")
        print()


def run_footage_download():
    """Download free stock footage for construction niche."""
    fd = FootageDownloader()
    fd.display_status()

    if not fd.pexels_key and not fd.pixabay_key:
        if HAS_RICH:
            console.print(Panel(
                "[bold yellow]FREE API Keys Needed[/]\n\n"
                "Get them in 30 seconds:\n\n"
                "1. [bold]Pexels[/] → https://www.pexels.com/api/\n"
                "   Sign up → Copy API key\n\n"
                "2. [bold]Pixabay[/] → https://pixabay.com/api/docs/\n"
                "   Sign up → Copy API key\n\n"
                "Then add to [bold]content_engine/.env[/]:\n"
                "  PEXELS_API_KEY=your-key\n"
                "  PIXABAY_API_KEY=your-key",
                title="[yellow]Setup Required[/]",
                border_style="yellow",
            ))
        else:
            print("\n  Get FREE API keys:")
            print("  Pexels: https://www.pexels.com/api/")
            print("  Pixabay: https://pixabay.com/api/docs/")
        return []

    if HAS_RICH:
        count = IntPrompt.ask("\n  Clips per query?", default=3)
        queries_count = IntPrompt.ask("  How many search queries?", default=5)
    else:
        count = int(input("\n  Clips per query [3]: ") or "3")
        queries_count = int(input("  How many queries [5]: ") or "5")

    queries = random.sample(SEARCH_QUERIES, min(queries_count, len(SEARCH_QUERIES)))

    if HAS_RICH:
        console.print(f"\n  [cyan]Downloading {count * len(queries)} clips...[/]\n")

    paths = fd.download_batch(queries=queries, clips_per_query=count)
    fd.save_log()

    if HAS_RICH:
        console.print(f"\n  [green]Done! {len(paths)} clips ready in: {Config.FOOTAGE_DIR}[/]")
    else:
        print(f"\n  Done! {len(paths)} clips in: {Config.FOOTAGE_DIR}")

    return paths


# Import search queries for the menu
from footage_downloader import SEARCH_QUERIES


    """Generate content ideas."""
    gen = IdeaGenerator()

    if HAS_RICH:
        count = IntPrompt.ask("\n  How many ideas to generate?", default=5)
    else:
        count = int(input("\n  How many ideas to generate? [5]: ") or "5")

    console.print() if HAS_RICH else print()

    ideas = gen.generate_batch(count)
    for idea in ideas:
        gen.display_idea(idea)

    # Save
    filepath = gen.save_ideas(ideas)
    if HAS_RICH:
        console.print(f"  [green]Saved {count} ideas to: {filepath}[/]\n")
    else:
        print(f"  Saved {count} ideas to: {filepath}\n")

    return ideas


def run_video_assembler(hook: str = None):
    """Assemble a video from footage."""
    va = VideoAssembler()

    clips = va.get_footage_clips()
    if not clips:
        if HAS_RICH:
            console.print(Panel(
                f"[yellow]No footage clips found![/]\n\n"
                f"Add your video clips (.mp4, .mov) to:\n"
                f"[bold]{Config.FOOTAGE_DIR}[/]\n\n"
                f"Then run this again.",
                title="[yellow]No Footage[/]",
                border_style="yellow",
            ))
        else:
            print(f"\n  No footage found. Add clips to: {Config.FOOTAGE_DIR}\n")
        return None

    if HAS_RICH:
        console.print(f"\n  [cyan]Found {len(clips)} clip(s). Assembling...[/]\n")
    else:
        print(f"\n  Found {len(clips)} clip(s). Assembling...\n")

    if not hook:
        hook = IdeaGenerator().generate_hook()

    output = va.assemble(hook=hook, max_duration=55)
    return output


def run_caption_optimizer(topic: str = None):
    """Generate optimized captions."""
    co = CaptionOptimizer()

    if not topic:
        if HAS_RICH:
            topic = Prompt.ask("\n  Build topic", default="house")
        else:
            topic = input("\n  Build topic [house]: ") or "house"

    if HAS_RICH:
        console.print(f"\n  [cyan]Generating caption variants for '{topic}'...[/]\n")
    else:
        print(f"\n  Generating captions for '{topic}'...\n")

    variants = co.generate_ab_variants(topic, count=3)
    for v in variants:
        co.display_caption(v)

    filepath = co.save_captions(variants)
    if HAS_RICH:
        console.print(f"  [green]Saved to: {filepath}[/]\n")
    else:
        print(f"  Saved to: {filepath}\n")

    return variants


def run_youtube_upload(video_path: str = None, title: str = None, caption: str = None):
    """Upload a video to YouTube Shorts."""
    yt = YouTubeUploader()

    if not yt.authenticate():
        return None

    yt.display_status()

    # Find video to upload
    if not video_path:
        # Look for the most recent output video
        if os.path.exists(Config.OUTPUT_DIR):
            videos = [f for f in os.listdir(Config.OUTPUT_DIR)
                      if f.endswith(".mp4") and f.startswith("short_")]
            if videos:
                videos.sort(reverse=True)
                video_path = os.path.join(Config.OUTPUT_DIR, videos[0])
                if HAS_RICH:
                    console.print(f"  [cyan]Using latest video: {videos[0]}[/]")
                else:
                    print(f"  Using latest video: {videos[0]}")

    if not video_path or not os.path.exists(video_path):
        if HAS_RICH:
            console.print("[red]  No video found to upload. Run Video Assembler first.[/]")
        else:
            print("  No video found. Run Video Assembler first.")
        return None

    # Generate title/caption if not provided
    if not title:
        co = CaptionOptimizer()
        title = co.generate_title()

    if not caption:
        co = CaptionOptimizer()
        caption_data = co.generate_full_caption()
        caption = caption_data.get("caption", "")

    if HAS_RICH:
        console.print(f"\n  [bold]Uploading:[/] {os.path.basename(video_path)}")
        console.print(f"  [bold]Title:[/] {title}")
        console.print()

    result = yt.upload_as_short(video_path, title, caption)
    return result


def run_full_pipeline():
    """Run the complete pipeline: idea → video → caption → upload."""
    if HAS_RICH:
        console.print(Panel(
            "[bold]Running Full Pipeline[/]\n"
            "[dim]Idea → Video → Caption → Upload[/]",
            border_style="magenta",
        ))
    else:
        print("\n  === Full Pipeline: Idea → Video → Caption → Upload ===\n")

    # Step 1: Generate idea
    if HAS_RICH:
        console.print("\n  [bold cyan]Step 1/4:[/] Generating content idea...")
    gen = IdeaGenerator()
    idea = gen.generate_script()
    gen.display_idea(idea)
    hook = idea.get("hook", "")
    topic = idea.get("title", "house").split()[0].lower()

    # Step 2: Assemble video
    if HAS_RICH:
        console.print("\n  [bold cyan]Step 2/4:[/] Assembling video...")
    video_path = run_video_assembler(hook=hook)

    if not video_path:
        if HAS_RICH:
            console.print("[yellow]  Pipeline paused - no footage available.[/]")
            console.print(f"  Add clips to [bold]{Config.FOOTAGE_DIR}[/] and try again.\n")
        else:
            print(f"  No footage. Add clips to {Config.FOOTAGE_DIR}")
        return

    # Step 3: Generate caption
    if HAS_RICH:
        console.print("\n  [bold cyan]Step 3/4:[/] Optimizing caption...")
    co = CaptionOptimizer()
    caption_data = co.generate_full_caption(topic)
    co.display_caption(caption_data)

    # Step 4: Upload
    if HAS_RICH:
        console.print("\n  [bold cyan]Step 4/4:[/] Uploading to YouTube...")

    result = run_youtube_upload(
        video_path=video_path,
        title=caption_data.get("title", ""),
        caption=caption_data.get("caption", ""),
    )

    if result:
        if HAS_RICH:
            console.print(Panel(
                f"[bold green]Pipeline Complete![/]\n\n"
                f"Video: {result.get('url', 'N/A')}\n"
                f"Title: {result.get('title', 'N/A')}",
                border_style="green",
                title="[bold]Success[/]",
            ))
    else:
        if HAS_RICH:
            console.print("[yellow]  Upload skipped (YouTube not configured).[/]")
            console.print(f"  Video saved at: [bold]{video_path}[/]\n")


def run_autopilot():
    """Run the fully autonomous pipeline on autopilot."""
    from auto_pipeline import AutoPipeline

    if HAS_RICH:
        console.print(Panel(
            "[bold white]AUTOPILOT MODE[/]\n"
            "[dim]Fully autonomous: generate → download → assemble → upload[/]\n"
            "[dim]Press Ctrl+C to stop[/]",
            border_style="red",
            title="[bold red]AUTONOMOUS[/]",
        ))
        interval = IntPrompt.ask("  Minutes between videos", default=60)
        max_videos = Prompt.ask("  Max videos (0 = unlimited)", default="0")
        max_videos = int(max_videos) if max_videos != "0" else None
    else:
        print("\n  AUTOPILOT MODE - Fully autonomous content generation")
        interval = int(input("  Minutes between videos [60]: ") or "60")
        max_input = input("  Max videos (0 = unlimited) [0]: ") or "0"
        max_videos = int(max_input) if max_input != "0" else None

    pipeline = AutoPipeline()
    pipeline.run_loop(interval_minutes=interval, max_runs=max_videos)


def run_tiktok_login():
    """Login to TikTok and save cookies."""
    try:
        from tiktok_uploader import TikTokUploader
        tt = TikTokUploader()
        if HAS_RICH:
            console.print("\n  [magenta]Opening browser for TikTok login...[/]")
            console.print("  [dim]Log in manually, cookies will be saved for auto-upload.[/]\n")
        else:
            print("\n  Opening browser for TikTok login...")
        tt.login(headless=False)
        tt.close()
    except Exception as e:
        if HAS_RICH:
            console.print(f"  [red]TikTok login error: {e}[/]")
        else:
            print(f"  TikTok login error: {e}")


def show_menu():
    """Show interactive menu."""
    if HAS_RICH:
        table = Table(show_header=False, box=box.ROUNDED, border_style="magenta", padding=(0, 2))
        table.add_column("", style="bold yellow", width=4)
        table.add_column("", style="white")

        table.add_row("1", "Generate Content Ideas (scripts, hooks, concepts)")
        table.add_row("2", "Download FREE Stock Footage (Pexels/Pixabay)")
        table.add_row("3", "Assemble Video (footage → Shorts-ready MP4)")
        table.add_row("4", "Optimize Captions & Hashtags")
        table.add_row("5", "Upload to YouTube Shorts")
        table.add_row("6", "Upload to TikTok")
        table.add_row("7", "Full Pipeline (download → assemble → caption → upload)")
        table.add_row("[red]8[/]", "[bold red]AUTOPILOT (auto-generate + auto-upload loop)[/]")
        table.add_row("9", "TikTok Login (save cookies for auto-upload)")
        table.add_row("S", "Show System Status")
        table.add_row("0", "Exit")

        console.print(Panel(table, title="[bold magenta]Menu[/]", border_style="magenta"))
        choice = Prompt.ask("  Select option", default="1")
    else:
        print("""
  ┌─── Menu ────────────────────────────────────────────┐
  │  [1] Generate Content Ideas                         │
  │  [2] Download FREE Stock Footage                    │
  │  [3] Assemble Video                                 │
  │  [4] Optimize Captions & Hashtags                   │
  │  [5] Upload to YouTube Shorts                       │
  │  [6] Upload to TikTok                               │
  │  [7] Full Pipeline (download → assemble → upload)   │
  │  [8] AUTOPILOT (auto-generate + auto-upload loop)   │
  │  [9] TikTok Login (save cookies)                    │
  │  [S] Show System Status                             │
  │  [0] Exit                                           │
  └─────────────────────────────────────────────────────┘
        """)
        choice = input("  Select option [1]: ") or "1"

    return choice.strip()


def interactive_mode():
    """Run in interactive menu mode."""
    while True:
        show_banner()
        show_status()
        choice = show_menu()

        if choice == "1":
            run_idea_generator()
            input("\n  Press Enter to continue...")
        elif choice == "2":
            run_footage_download()
            input("\n  Press Enter to continue...")
        elif choice == "3":
            run_video_assembler()
            input("\n  Press Enter to continue...")
        elif choice == "4":
            run_caption_optimizer()
            input("\n  Press Enter to continue...")
        elif choice == "5":
            run_youtube_upload()
            input("\n  Press Enter to continue...")
        elif choice == "6":
            # TikTok upload
            try:
                from tiktok_uploader import TikTokUploader
                tt = TikTokUploader()
                # Find latest video
                if os.path.exists(Config.OUTPUT_DIR):
                    videos = [f for f in os.listdir(Config.OUTPUT_DIR) if f.endswith(".mp4")]
                    if videos:
                        videos.sort(reverse=True)
                        video_path = os.path.join(Config.OUTPUT_DIR, videos[0])
                        co = CaptionOptimizer()
                        caption_data = co.generate_full_caption()
                        tt.upload(video_path, caption=caption_data.get("caption", ""))
                    else:
                        print("  No video found. Assemble one first.")
                tt.close()
            except Exception as e:
                print(f"  TikTok error: {e}")
            input("\n  Press Enter to continue...")
        elif choice == "7":
            run_full_pipeline()
            input("\n  Press Enter to continue...")
        elif choice == "8":
            run_autopilot()
            input("\n  Press Enter to continue...")
        elif choice == "9":
            run_tiktok_login()
            input("\n  Press Enter to continue...")
        elif choice.lower() == "s":
            show_status()
            input("\n  Press Enter to continue...")
        elif choice == "0":
            if HAS_RICH:
                console.print("\n  [dim]Goodbye![/]\n")
            else:
                print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            if HAS_RICH:
                console.print("[red]  Invalid option.[/]")
            time.sleep(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Content Engine - Mini Building Construction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--ideas", action="store_true", help="Generate content ideas")
    parser.add_argument("--video", action="store_true", help="Assemble a video")
    parser.add_argument("--caption", action="store_true", help="Generate captions")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube")
    parser.add_argument("--full", action="store_true", help="Run full pipeline")
    parser.add_argument("--autopilot", action="store_true", help="Run autonomous auto-generate + auto-upload loop")
    parser.add_argument("--every", type=int, default=60, help="Minutes between autopilot runs (default: 60)")
    parser.add_argument("--count", type=int, default=None, help="Max videos in autopilot mode")
    parser.add_argument("--topic", type=str, default=None, help="Build topic")

    args = parser.parse_args()

    Config.ensure_dirs()

    if args.autopilot:
        show_banner()
        from auto_pipeline import AutoPipeline
        pipeline = AutoPipeline()
        pipeline.run_loop(interval_minutes=args.every, max_runs=args.count)
    elif args.ideas:
        show_banner()
        run_idea_generator()
    elif args.video:
        show_banner()
        run_video_assembler()
    elif args.caption:
        show_banner()
        run_caption_optimizer(topic=args.topic)
    elif args.upload:
        show_banner()
        run_youtube_upload()
    elif args.full:
        show_banner()
        run_full_pipeline()
    else:
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\n\n  Stopped. Goodbye!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
