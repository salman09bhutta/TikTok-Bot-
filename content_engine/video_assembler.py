"""
Video Assembler Module
========================
Takes user footage clips and assembles them into vertical Shorts-ready videos
with subtitles, background music, transitions, and effects using FFmpeg/MoviePy.

Features:
- Combines multiple clips into one vertical video (9:16)
- Adds animated subtitles/captions
- Overlays background music with fade in/out
- Applies transitions (crossfade, fade to black)
- Adds hook text overlay at the start
- Auto-crops horizontal footage to vertical
- Exports optimized for TikTok/YouTube Shorts

Usage:
    from video_assembler import VideoAssembler
    va = VideoAssembler()
    va.assemble("output.mp4", clips=["clip1.mp4", "clip2.mp4"], hook="Watch this!")
"""

import os
import subprocess
import json
import random
from datetime import datetime
from config import Config

try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip, CompositeAudioClip,
        vfx, afx
    )
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def _log(msg):
    if HAS_RICH:
        console.print(f"  [cyan][VIDEO][/] {msg}")
    else:
        print(f"  [VIDEO] {msg}")


def _check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


class VideoAssembler:
    """Assembles vertical short videos from footage clips."""

    def __init__(self):
        Config.ensure_dirs()
        self.has_ffmpeg = _check_ffmpeg()
        self.has_moviepy = HAS_MOVIEPY

        if not self.has_ffmpeg:
            _log("[yellow]FFmpeg not found. Install from https://ffmpeg.org[/]")
        if not self.has_moviepy:
            _log("[yellow]MoviePy not available. Install: pip install moviepy[/]")

    def get_footage_clips(self) -> list:
        """List available footage clips in the footage directory."""
        clips = []
        if os.path.exists(Config.FOOTAGE_DIR):
            for f in sorted(os.listdir(Config.FOOTAGE_DIR)):
                if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
                    clips.append(os.path.join(Config.FOOTAGE_DIR, f))
        return clips

    def get_music_tracks(self) -> list:
        """List available background music tracks."""
        tracks = []
        if os.path.exists(Config.MUSIC_DIR):
            for f in sorted(os.listdir(Config.MUSIC_DIR)):
                if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg", ".aac")):
                    tracks.append(os.path.join(Config.MUSIC_DIR, f))
        return tracks

    def crop_to_vertical(self, clip):
        """Crop a horizontal clip to 9:16 vertical (center crop)."""
        w, h = clip.size
        target_ratio = 9 / 16

        current_ratio = w / h
        if current_ratio > target_ratio:
            # Wider than 9:16 - crop sides
            new_w = int(h * target_ratio)
            x_offset = (w - new_w) // 2
            clip = clip.crop(x1=x_offset, x2=x_offset + new_w)
        elif current_ratio < target_ratio:
            # Taller than 9:16 - crop top/bottom
            new_h = int(w / target_ratio)
            y_offset = (h - new_h) // 2
            clip = clip.crop(y1=y_offset, y2=y_offset + new_h)

        # Resize to target resolution
        clip = clip.resize((Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT))
        return clip

    def create_text_overlay(self, text: str, duration: float, position="center",
                            fontsize=60, color="white", stroke_color="black",
                            stroke_width=3) -> 'TextClip':
        """Create a text overlay clip."""
        if not HAS_MOVIEPY:
            return None

        try:
            txt_clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method="caption",
                size=(Config.VIDEO_WIDTH - 100, None),
                align="center",
            )
            txt_clip = txt_clip.set_duration(duration).set_position(position)
            return txt_clip
        except Exception as e:
            _log(f"Text overlay failed: {e}")
            return None

    def create_subtitle_clips(self, subtitles: list, start_time: float = 0) -> list:
        """
        Create subtitle overlay clips.

        Args:
            subtitles: List of dicts with 'text', 'start', 'end' keys
            start_time: Offset for subtitle timing

        Returns:
            List of TextClip objects
        """
        if not HAS_MOVIEPY:
            return []

        clips = []
        for sub in subtitles:
            try:
                txt = TextClip(
                    sub["text"],
                    fontsize=48,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(Config.VIDEO_WIDTH - 80, None),
                    align="center",
                )
                txt = (txt
                       .set_start(sub["start"] + start_time)
                       .set_end(sub["end"] + start_time)
                       .set_position(("center", Config.VIDEO_HEIGHT - 300)))
                clips.append(txt)
            except Exception:
                continue

        return clips

    def assemble(self, output_filename: str = None, clips: list = None,
                 hook: str = None, subtitles: list = None,
                 music_track: str = None, music_volume: float = 0.15,
                 max_duration: int = None) -> str:
        """
        Assemble a complete vertical short video.

        Args:
            output_filename: Output file path (auto-generated if None)
            clips: List of video file paths (uses footage dir if None)
            hook: Text to overlay at the start (first 3 seconds)
            subtitles: List of subtitle dicts [{"text": "...", "start": 0, "end": 3}]
            music_track: Path to background music (random from music dir if None)
            music_volume: Volume of background music (0.0 - 1.0)
            max_duration: Maximum video duration in seconds

        Returns:
            Path to the assembled video file
        """
        if not HAS_MOVIEPY:
            _log("[red]MoviePy required. Install: pip install moviepy[/]")
            return self._assemble_ffmpeg_only(output_filename, clips, hook, music_track, max_duration)

        max_duration = max_duration or Config.VIDEO_MAX_DURATION

        # Get clips
        if not clips:
            clips = self.get_footage_clips()
        if not clips:
            _log("[red]No footage clips found! Add videos to: " + Config.FOOTAGE_DIR)
            return None

        _log(f"Assembling video from {len(clips)} clip(s)...")

        # Load and process clips
        video_clips = []
        total_duration = 0

        for clip_path in clips:
            if total_duration >= max_duration:
                break

            try:
                _log(f"Loading: {os.path.basename(clip_path)}")
                clip = VideoFileClip(clip_path)

                # Crop to vertical
                clip = self.crop_to_vertical(clip)

                # Trim if too long
                remaining = max_duration - total_duration
                if clip.duration > remaining:
                    clip = clip.subclip(0, remaining)

                # Add crossfade transition
                if video_clips:
                    clip = clip.crossfadein(0.5)

                video_clips.append(clip)
                total_duration += clip.duration

            except Exception as e:
                _log(f"[yellow]Skipping {os.path.basename(clip_path)}: {e}[/]")
                continue

        if not video_clips:
            _log("[red]No clips could be loaded![/]")
            return None

        # Concatenate clips
        _log("Concatenating clips...")
        final_video = concatenate_videoclips(video_clips, method="compose")

        # Add hook text overlay
        overlays = [final_video]
        if hook:
            _log(f"Adding hook: '{hook[:40]}...'")
            hook_clip = self.create_text_overlay(
                hook, duration=3.5, position=("center", "center"),
                fontsize=65, color="white", stroke_width=4
            )
            if hook_clip:
                hook_clip = hook_clip.set_start(0).crossfadein(0.3).crossfadeout(0.3)
                overlays.append(hook_clip)

        # Add subtitles
        if subtitles:
            _log(f"Adding {len(subtitles)} subtitle(s)...")
            sub_clips = self.create_subtitle_clips(subtitles)
            overlays.extend(sub_clips)

        # Composite all overlays
        if len(overlays) > 1:
            final_video = CompositeVideoClip(overlays)

        # Add background music
        if music_track is None:
            tracks = self.get_music_tracks()
            if tracks:
                music_track = random.choice(tracks)

        if music_track and os.path.exists(music_track):
            _log(f"Adding music: {os.path.basename(music_track)}")
            try:
                audio = AudioFileClip(music_track)
                # Loop/trim music to match video duration
                if audio.duration < final_video.duration:
                    # Loop music
                    loops_needed = int(final_video.duration / audio.duration) + 1
                    audio = audio.audio_loop(nloops=loops_needed)
                audio = audio.subclip(0, final_video.duration)
                audio = audio.volumex(music_volume)

                # Fade in/out
                audio = audio.audio_fadein(1.0).audio_fadeout(2.0)

                # Mix with original audio
                if final_video.audio:
                    final_audio = CompositeAudioClip([final_video.audio, audio])
                else:
                    final_audio = audio

                final_video = final_video.set_audio(final_audio)
            except Exception as e:
                _log(f"[yellow]Music overlay failed: {e}[/]")

        # Generate output path
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = os.path.join(Config.OUTPUT_DIR, f"short_{timestamp}.mp4")

        # Export
        _log(f"Exporting: {output_filename}")
        _log(f"Duration: {final_video.duration:.1f}s | Resolution: {Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}")

        final_video.write_videofile(
            output_filename,
            fps=Config.VIDEO_FPS,
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            threads=4,
            logger=None,  # Suppress moviepy progress bars
        )

        # Cleanup
        for clip in video_clips:
            clip.close()
        final_video.close()

        file_size = os.path.getsize(output_filename) / (1024 * 1024)
        _log(f"[green]Done! Output: {output_filename} ({file_size:.1f} MB)[/]")
        return output_filename

    def _assemble_ffmpeg_only(self, output_filename=None, clips=None,
                              hook=None, music_track=None, max_duration=None) -> str:
        """Fallback: assemble using pure FFmpeg commands."""
        if not self.has_ffmpeg:
            _log("[red]FFmpeg not installed. Cannot assemble video.[/]")
            return None

        if not clips:
            clips = self.get_footage_clips()
        if not clips:
            _log("[red]No footage clips found![/]")
            return None

        max_duration = max_duration or Config.VIDEO_MAX_DURATION

        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = os.path.join(Config.OUTPUT_DIR, f"short_{timestamp}.mp4")

        Config.ensure_dirs()

        # Create concat file
        concat_file = os.path.join(Config.OUTPUT_DIR, "_concat.txt")
        with open(concat_file, "w") as f:
            for clip in clips:
                f.write(f"file '{os.path.abspath(clip)}'\n")

        _log(f"Assembling {len(clips)} clips with FFmpeg...")

        # FFmpeg command: concat + crop to vertical + limit duration
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_file,
            "-vf", f"crop=ih*9/16:ih,scale={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}",
            "-t", str(max_duration),
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k",
            "-r", str(Config.VIDEO_FPS),
            "-movflags", "+faststart",
            output_filename,
        ]

        # Add hook text with drawtext filter
        if hook:
            # Escape special characters for FFmpeg
            safe_hook = hook.replace("'", "'\\''").replace(":", "\\:")
            drawtext = (
                f"drawtext=text='{safe_hook}':fontsize=50:fontcolor=white:"
                f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:"
                f"enable='between(t,0,3.5)'"
            )
            # Update -vf filter
            cmd[cmd.index("-vf") + 1] = (
                f"crop=ih*9/16:ih,scale={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT},{drawtext}"
            )

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Cleanup concat file
        if os.path.exists(concat_file):
            os.remove(concat_file)

        if result.returncode == 0 and os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename) / (1024 * 1024)
            _log(f"[green]Done! Output: {output_filename} ({file_size:.1f} MB)[/]")
            return output_filename
        else:
            _log(f"[red]FFmpeg failed: {result.stderr[-200:] if result.stderr else 'unknown error'}[/]")
            return None

    def create_blank_with_text(self, text: str, duration: float = 5,
                               output_filename: str = None) -> str:
        """Create a simple video with text on a dark background (for testing)."""
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = os.path.join(Config.OUTPUT_DIR, f"text_{timestamp}.mp4")

        Config.ensure_dirs()

        if self.has_ffmpeg:
            safe_text = text.replace("'", "'\\''").replace(":", "\\:")
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i",
                f"color=c=0x1a1a2e:s={Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}:d={duration}",
                "-vf",
                f"drawtext=text='{safe_text}':fontsize=55:fontcolor=white:"
                f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-r", str(Config.VIDEO_FPS),
                output_filename,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                _log(f"Created text video: {output_filename}")
                return output_filename

        _log("[red]Could not create video[/]")
        return None


# ═══════════════════════════════════════════════════════════
# Standalone usage
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    va = VideoAssembler()

    print("\n  Video Assembler - Mini Building Construction")
    print("  " + "=" * 50)
    print(f"  FFmpeg available: {'Yes' if va.has_ffmpeg else 'No'}")
    print(f"  MoviePy available: {'Yes' if va.has_moviepy else 'No'}")

    clips = va.get_footage_clips()
    tracks = va.get_music_tracks()
    print(f"  Footage clips: {len(clips)}")
    print(f"  Music tracks: {len(tracks)}")

    if clips:
        print("\n  Assembling video...")
        output = va.assemble(
            hook="Watch me build a tiny house from scratch",
            max_duration=45,
        )
        if output:
            print(f"\n  Output: {output}")
    else:
        print(f"\n  Add footage clips to: {Config.FOOTAGE_DIR}")
        print("  Then run again to assemble!")

        # Demo: create a text-only video
        print("\n  Creating demo text video...")
        demo = va.create_blank_with_text(
            "Mini Building\nConstruction",
            duration=5,
        )
        if demo:
            print(f"  Demo: {demo}")
