"""
YouTube Shorts Auto-Uploader Module
======================================
Uploads videos to YouTube as Shorts and schedules them using YouTube Data API v3.

Setup:
1. Go to https://console.cloud.google.com
2. Create a project → Enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop App)
4. Download client_secrets.json and place in content_engine/
5. First run will open browser for auth (creates token.json)

Usage:
    from youtube_uploader import YouTubeUploader
    yt = YouTubeUploader()
    yt.authenticate()
    yt.upload("video.mp4", title="Mini House Build", description="...")
"""

import os
import json
import time
import datetime
from config import Config

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    HAS_YOUTUBE_API = True
except ImportError:
    HAS_YOUTUBE_API = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def _log(msg):
    if HAS_RICH:
        console.print(f"  [magenta][YOUTUBE][/] {msg}")
    else:
        print(f"  [YOUTUBE] {msg}")


# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
           "https://www.googleapis.com/auth/youtube"]

# Shorts category: People & Blogs (22) or Entertainment (24) or Howto & Style (26)
CATEGORY_HOWTO = "26"
CATEGORY_ENTERTAINMENT = "24"

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")


class YouTubeUploader:
    """Handles YouTube Shorts upload and scheduling."""

    def __init__(self):
        self.service = None
        self.authenticated = False
        self.uploads_today = 0

        if not HAS_YOUTUBE_API:
            _log("[yellow]YouTube API libraries not installed.[/]")
            _log("[yellow]Install: pip install google-api-python-client google-auth-oauthlib[/]")

    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API using OAuth 2.0.
        First run opens browser for authorization.
        Subsequent runs use saved token.

        Returns:
            True if authentication succeeded
        """
        if not HAS_YOUTUBE_API:
            _log("[red]YouTube API libraries required.[/]")
            return False

        credentials = None

        # Load existing token
        if os.path.exists(TOKEN_FILE):
            try:
                credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            except Exception:
                pass

        # Refresh or get new token
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    _log("Refreshing OAuth token...")
                    credentials.refresh(Request())
                except Exception:
                    credentials = None

            if not credentials:
                client_secrets = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    Config.YOUTUBE_CLIENT_SECRETS_FILE
                )

                if not os.path.exists(client_secrets):
                    _log(f"[red]client_secrets.json not found at: {client_secrets}[/]")
                    _log("[yellow]Download from Google Cloud Console → APIs → Credentials[/]")
                    _log("[yellow]Create OAuth 2.0 Client ID (Desktop App)[/]")
                    return False

                _log("Opening browser for YouTube authorization...")
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
                credentials = flow.run_local_server(port=8080)

            # Save token for next time
            with open(TOKEN_FILE, "w") as f:
                f.write(credentials.to_json())
            _log("[green]Token saved for future use.[/]")

        # Build YouTube service
        self.service = build("youtube", "v3", credentials=credentials)
        self.authenticated = True
        _log("[green]Authenticated with YouTube API![/]")
        return True

    def upload(self, video_path: str, title: str, description: str = "",
               tags: list = None, category: str = CATEGORY_HOWTO,
               privacy: str = "public", scheduled_time: str = None) -> dict:
        """
        Upload a video to YouTube as a Short.

        Args:
            video_path: Path to the video file
            title: Video title (max 100 chars, must include #Shorts)
            description: Video description
            tags: List of tags/keywords
            category: YouTube category ID (26 = Howto & Style)
            privacy: "public", "unlisted", or "private"
            scheduled_time: ISO 8601 datetime to publish (for scheduled uploads)

        Returns:
            Dict with video ID and URL if successful, None otherwise
        """
        if not self.authenticated:
            _log("[red]Not authenticated. Call authenticate() first.[/]")
            return None

        if not os.path.exists(video_path):
            _log(f"[red]Video file not found: {video_path}[/]")
            return None

        # Ensure title includes #Shorts for YouTube to recognize it
        if "#Shorts" not in title and "#shorts" not in title:
            title = f"{title} #Shorts"

        # Truncate title to 100 chars
        if len(title) > 100:
            title = title[:97] + "..."

        # Default tags for construction niche
        if tags is None:
            tags = [
                "shorts", "mini building", "miniature construction",
                "satisfying", "diy", "cement craft", "tiny house",
                "construction", "mini", "asmr", "timelapse",
            ]

        # Add #Shorts to description
        if "#Shorts" not in description:
            description += "\n\n#Shorts #MiniBuilding #Construction"

        _log(f"Uploading: {os.path.basename(video_path)}")
        _log(f"Title: {title}")

        # Set privacy for scheduled uploads
        if scheduled_time:
            privacy = "private"  # Must be private until publish time

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        # Add scheduled publish time
        if scheduled_time:
            body["status"]["publishAt"] = scheduled_time
            body["status"]["privacyStatus"] = "private"
            _log(f"Scheduled for: {scheduled_time}")

        # Upload with resumable media
        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=10 * 1024 * 1024,  # 10MB chunks
        )

        try:
            request = self.service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    _log(f"Upload progress: {progress}%")

            video_id = response["id"]
            video_url = f"https://youtube.com/shorts/{video_id}"

            self.uploads_today += 1
            _log(f"[green]Upload complete![/]")
            _log(f"[green]URL: {video_url}[/]")

            return {
                "video_id": video_id,
                "url": video_url,
                "title": title,
                "status": privacy,
                "scheduled": scheduled_time,
            }

        except Exception as e:
            _log(f"[red]Upload failed: {e}[/]")
            return None

    def upload_as_short(self, video_path: str, title: str, description: str = "",
                        tags: list = None) -> dict:
        """Convenience method - upload specifically as a YouTube Short."""
        return self.upload(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            category=CATEGORY_HOWTO,
            privacy="public",
        )

    def schedule_upload(self, video_path: str, title: str, description: str = "",
                        tags: list = None, publish_at: datetime.datetime = None) -> dict:
        """
        Schedule a video upload for future publication.

        Args:
            video_path: Path to video
            title: Video title
            description: Description
            tags: Tags list
            publish_at: When to publish (datetime object)

        Returns:
            Upload result dict
        """
        if publish_at is None:
            # Default: schedule for next available slot
            now = datetime.datetime.now(datetime.timezone.utc)
            publish_at = now + datetime.timedelta(hours=2)

        # Format as ISO 8601
        scheduled_time = publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        return self.upload(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            scheduled_time=scheduled_time,
        )

    def get_channel_info(self) -> dict:
        """Get basic channel information."""
        if not self.authenticated:
            return None

        try:
            response = self.service.channels().list(
                part="snippet,statistics",
                mine=True,
            ).execute()

            if response["items"]:
                channel = response["items"][0]
                return {
                    "name": channel["snippet"]["title"],
                    "id": channel["id"],
                    "subscribers": channel["statistics"].get("subscriberCount", "0"),
                    "videos": channel["statistics"].get("videoCount", "0"),
                    "views": channel["statistics"].get("viewCount", "0"),
                }
        except Exception as e:
            _log(f"[yellow]Could not get channel info: {e}[/]")

        return None

    def get_upload_schedule(self) -> list:
        """Generate upload schedule based on config."""
        schedule_times = []
        today = datetime.date.today()

        for time_str in Config.POST_TIMES:
            try:
                hour, minute = map(int, time_str.strip().split(":"))
                publish_time = datetime.datetime(
                    today.year, today.month, today.day,
                    hour, minute, 0,
                    tzinfo=datetime.timezone.utc,
                )
                # If time already passed today, schedule for tomorrow
                if publish_time < datetime.datetime.now(datetime.timezone.utc):
                    publish_time += datetime.timedelta(days=1)
                schedule_times.append(publish_time)
            except ValueError:
                continue

        return schedule_times

    def display_status(self):
        """Display upload status and channel info."""
        if HAS_RICH:
            if self.authenticated:
                info = self.get_channel_info()
                if info:
                    table = Table(show_header=False, box=box.SIMPLE)
                    table.add_column("Key", style="bold cyan")
                    table.add_column("Value", style="white")
                    table.add_row("Channel", info["name"])
                    table.add_row("Subscribers", info["subscribers"])
                    table.add_row("Total Videos", info["videos"])
                    table.add_row("Total Views", info["views"])
                    table.add_row("Uploads Today", str(self.uploads_today))
                    console.print(Panel(table, title="[bold green]YouTube Status[/]", border_style="green"))
                else:
                    console.print("[green]  Authenticated (channel info unavailable)[/]")
            else:
                console.print(Panel(
                    "[yellow]Not authenticated. Run authenticate() first.[/]\n"
                    "[dim]Need: client_secrets.json from Google Cloud Console[/]",
                    title="[yellow]YouTube Status[/]",
                    border_style="yellow",
                ))
        else:
            print(f"  YouTube: {'Authenticated' if self.authenticated else 'Not connected'}")
            print(f"  Uploads today: {self.uploads_today}")


# ═══════════════════════════════════════════════════════════
# Standalone usage
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    yt = YouTubeUploader()

    print("\n  YouTube Shorts Uploader - Mini Building Construction")
    print("  " + "=" * 55)

    if not HAS_YOUTUBE_API:
        print("\n  Install required packages:")
        print("  pip install google-api-python-client google-auth-oauthlib")
    else:
        print(f"  API libraries: Installed")
        print(f"  Token file: {'Found' if os.path.exists(TOKEN_FILE) else 'Not found (will auth on first upload)'}")
        print(f"  Client secrets: {'Found' if os.path.exists(Config.YOUTUBE_CLIENT_SECRETS_FILE) else 'Missing - download from Google Cloud'}")

        # Show upload schedule
        schedule = yt.get_upload_schedule()
        print(f"\n  Upload Schedule ({Config.POSTS_PER_DAY} posts/day):")
        for t in schedule:
            print(f"    - {t.strftime('%Y-%m-%d %H:%M UTC')}")

        print("\n  To upload a video:")
        print("    yt = YouTubeUploader()")
        print("    yt.authenticate()")
        print('    yt.upload_as_short("output/short.mp4", "Mini House Build")')
