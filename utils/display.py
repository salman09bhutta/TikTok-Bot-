"""
Display & Theme Module for TikTok Bot.
Provides rich terminal UI with colors, tables, progress bars, and banners.
"""

import os
import sys
import time
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.live import Live
    from rich.layout import Layout
    from rich.columns import Columns
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    from pyfiglet import Figlet
    HAS_FIGLET = True
except ImportError:
    HAS_FIGLET = False

from colorama import Fore, Back, Style, init
init(autoreset=True)

console = Console() if HAS_RICH else None


# ═══════════════════════════════════════════════════════════
# Theme Colors
# ═══════════════════════════════════════════════════════════
THEME = {
    "primary": "cyan",
    "secondary": "magenta",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "accent": "bright_magenta",
    "muted": "dim white",
}


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def show_banner():
    """Display the main TikTok Bot banner with ASCII art."""
    clear_screen()

    if HAS_RICH and HAS_FIGLET:
        fig = Figlet(font="slant")
        ascii_art = fig.renderText("TikTok Bot")

        banner_text = Text(ascii_art, style="bold cyan")
        console.print(banner_text)
        console.print(
            Panel(
                "[bold magenta]US Views[/] | [bold green]Followers[/] | "
                "[bold yellow]Likes[/] | [bold cyan]Engagement[/]\n"
                "[dim]Automated TikTok Growth from United States Traffic[/]",
                border_style="cyan",
                title="[bold white]v2.0[/]",
                subtitle="[dim]github.com/salman09bhutta/TikTok-Bot-[/]",
            )
        )
    else:
        print(f"""
{Fore.CYAN}
  ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗    ██████╗  ██████╗ ████████╗
  ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
     ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝     ██████╔╝██║   ██║   ██║
     ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗     ██╔══██╗██║   ██║   ██║
     ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗    ██████╔╝╚██████╔╝   ██║
     ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝
{Style.RESET_ALL}
{Fore.WHITE}  ┌─────────────────────────────────────────────────────────────────────┐
  │  {Fore.MAGENTA}US Views{Fore.WHITE} │ {Fore.GREEN}Followers{Fore.WHITE} │ {Fore.YELLOW}Likes{Fore.WHITE} │ {Fore.CYAN}Engagement{Fore.WHITE}                      │
  │  {Fore.WHITE}Automated TikTok Growth from United States Traffic{Fore.WHITE}                │
  └─────────────────────────────────────────────────────────────────────┘
{Style.RESET_ALL}""")


def show_config_panel(username: str, proxy_count: int, headless: bool):
    """Display bot configuration in a styled panel."""
    if HAS_RICH:
        config_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        config_table.add_column("Key", style="bold cyan")
        config_table.add_column("Value", style="white")

        config_table.add_row("Target", f"@{username}")
        config_table.add_row("US Proxies", f"{proxy_count} loaded")
        config_table.add_row("Mode", "Headless" if headless else "Visible")
        config_table.add_row("Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        console.print(Panel(
            config_table,
            title="[bold green]Configuration[/]",
            border_style="green",
        ))
    else:
        print(f"""
{Fore.GREEN}  ┌─── Configuration ─────────────────────────┐
  │  Target:     {Fore.WHITE}@{username}{Fore.GREEN}
  │  US Proxies: {Fore.WHITE}{proxy_count} loaded{Fore.GREEN}
  │  Mode:       {Fore.WHITE}{'Headless' if headless else 'Visible'}{Fore.GREEN}
  │  Time:       {Fore.WHITE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Fore.GREEN}
  └──────────────────────────────────────────────┘{Style.RESET_ALL}
""")


def show_video_links(links: list, username: str):
    """Display discovered video links in a beautiful table."""
    if not links:
        if HAS_RICH:
            console.print("[yellow]  No videos found on profile.[/]")
        else:
            print(f"{Fore.YELLOW}  No videos found on profile.{Style.RESET_ALL}")
        return

    if HAS_RICH:
        table = Table(
            title=f"[bold cyan]Videos Found on @{username}[/]",
            box=box.ROUNDED,
            border_style="cyan",
            show_lines=True,
            header_style="bold magenta",
        )
        table.add_column("#", style="bold white", width=4, justify="center")
        table.add_column("Video URL", style="blue")
        table.add_column("Status", style="green", width=10, justify="center")

        for i, link in enumerate(links[:20], 1):  # Show max 20
            # Shorten the URL for display
            short_url = link if len(link) <= 60 else link[:57] + "..."
            table.add_row(
                str(i),
                short_url,
                "[green]Ready[/]"
            )

        if len(links) > 20:
            table.add_row("...", f"[dim]+{len(links) - 20} more videos[/]", "[dim]...[/]")

        console.print(table)
        console.print(f"\n  [bold green]Total: {len(links)} videos discovered[/]\n")
    else:
        print(f"\n{Fore.CYAN}  ╔═══ Videos Found on @{username} ═══{'═' * max(0, 40 - len(username))}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  ║ {'#':<4} {'Video URL':<58} {'Status':<8} ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  ╠{'═' * 74}╣{Style.RESET_ALL}")

        for i, link in enumerate(links[:15], 1):
            short_url = link if len(link) <= 55 else link[:52] + "..."
            print(f"{Fore.CYAN}  ║ {Fore.WHITE}{i:<4} {Fore.BLUE}{short_url:<58} {Fore.GREEN}{'Ready':<8} {Fore.CYAN}║{Style.RESET_ALL}")

        if len(links) > 15:
            print(f"{Fore.CYAN}  ║ {Fore.WHITE}...  {Fore.YELLOW}+{len(links) - 15} more videos{' ' * 40} {Fore.CYAN}║{Style.RESET_ALL}")

        print(f"{Fore.CYAN}  ╚{'═' * 74}╝{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}  Total: {len(links)} videos discovered{Style.RESET_ALL}\n")


def show_session_start(bot_type: str, target: int):
    """Display session start with animation."""
    if HAS_RICH:
        emoji_map = {
            "views": "👁️",
            "likes": "❤️",
            "follows": "👥",
            "engagement": "🔥",
        }
        emoji = emoji_map.get(bot_type, "🤖")

        console.print(Panel(
            f"[bold]{emoji} Starting {bot_type.upper()} session[/]\n"
            f"[dim]Target: {target} | Using US proxies[/]",
            border_style=THEME["primary"],
            title=f"[bold {THEME['accent']}]Session Active[/]",
        ))
    else:
        icon_map = {"views": ">>", "likes": "<3", "follows": "+1", "engagement": "**"}
        icon = icon_map.get(bot_type, ">>")
        print(f"\n{Fore.CYAN}  ┌─── {icon} {bot_type.upper()} Session ───────────────────────┐")
        print(f"  │  Target: {target} | Using US proxies       │")
        print(f"  └────────────────────────────────────────────────┘{Style.RESET_ALL}\n")


def show_action(action: str, detail: str, count: int = None):
    """Display a bot action in real-time."""
    timestamp = datetime.now().strftime("%H:%M:%S")

    if HAS_RICH:
        color_map = {
            "VIEW": "cyan",
            "LIKE": "red",
            "FOLLOW": "green",
            "PROXY": "yellow",
            "WATCH": "blue",
            "NAVIGATE": "magenta",
            "ERROR": "red",
            "SUCCESS": "green",
        }
        color = color_map.get(action.upper(), "white")
        count_str = f" [bold]#{count}[/]" if count else ""
        console.print(
            f"  [{THEME['muted']}]{timestamp}[/] "
            f"[bold {color}][{action.upper()}][/]{count_str} "
            f"{detail}"
        )
    else:
        color_map = {
            "VIEW": Fore.CYAN,
            "LIKE": Fore.RED,
            "FOLLOW": Fore.GREEN,
            "PROXY": Fore.YELLOW,
            "WATCH": Fore.BLUE,
            "NAVIGATE": Fore.MAGENTA,
            "ERROR": Fore.RED,
            "SUCCESS": Fore.GREEN,
        }
        color = color_map.get(action.upper(), Fore.WHITE)
        count_str = f" #{count}" if count else ""
        print(f"  {Fore.WHITE}{timestamp} {color}[{action.upper()}]{count_str}{Style.RESET_ALL} {detail}")


def show_progress_bar(current: int, total: int, label: str = "Progress"):
    """Display a simple progress indicator."""
    if HAS_RICH:
        percentage = (current / total * 100) if total > 0 else 0
        bar_width = 30
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        console.print(
            f"  [{THEME['muted']}]{label}:[/] "
            f"[{THEME['primary']}]{bar}[/] "
            f"[bold white]{current}/{total}[/] "
            f"[{THEME['muted']}]({percentage:.0f}%)[/]"
        )
    else:
        percentage = (current / total * 100) if total > 0 else 0
        bar_width = 25
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"  {Fore.WHITE}{label}: {Fore.CYAN}{bar}{Style.RESET_ALL} {current}/{total} ({percentage:.0f}%)")


def show_session_summary(bot_type: str, count: int, duration: float = None):
    """Display session completion summary."""
    if HAS_RICH:
        duration_str = f" in {duration:.0f}s" if duration else ""
        console.print(Panel(
            f"[bold green]Session Complete![/]\n"
            f"[white]{bot_type.title()}: [bold]{count}[/] generated{duration_str}[/]",
            border_style="green",
        ))
    else:
        duration_str = f" in {duration:.0f}s" if duration else ""
        print(f"\n{Fore.GREEN}  ✓ {bot_type.title()} Session Complete! {count} generated{duration_str}{Style.RESET_ALL}\n")


def show_stats_panel(stats: dict):
    """Display statistics in a beautiful panel."""
    if HAS_RICH:
        table = Table(box=box.DOUBLE_EDGE, border_style="cyan", header_style="bold magenta")
        table.add_column("Metric", style="bold white")
        table.add_column("All-Time", style="cyan", justify="right")
        table.add_column("Today", style="green", justify="right")

        today = datetime.now().strftime("%Y-%m-%d")
        daily = stats.get("daily_stats", {}).get(today, {})

        table.add_row(
            "Views",
            str(stats.get("total_views", 0)),
            str(daily.get("views", 0))
        )
        table.add_row(
            "Likes",
            str(stats.get("total_likes", 0)),
            str(daily.get("likes", 0))
        )
        table.add_row(
            "Follows",
            str(stats.get("total_follows", 0)),
            str(daily.get("follows", 0))
        )
        table.add_row(
            "Sessions",
            str(stats.get("sessions_completed", 0)),
            str(daily.get("sessions", 0))
        )

        console.print(Panel(
            table,
            title="[bold cyan]Performance Stats[/]",
            border_style="cyan",
            subtitle=f"[dim]Since {stats.get('first_run', 'N/A')[:10]}[/]",
        ))
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        daily = stats.get("daily_stats", {}).get(today, {})

        print(f"""
{Fore.CYAN}  ╔══════════════════════════════════════════════════╗
  ║          {Fore.WHITE}PERFORMANCE STATS{Fore.CYAN}                       ║
  ╠══════════════════════════════════════════════════╣
  ║  {Fore.WHITE}Metric      All-Time     Today{Fore.CYAN}                 ║
  ║  {Fore.CYAN}Views       {Fore.WHITE}{stats.get('total_views', 0):<12} {Fore.GREEN}{daily.get('views', 0):<8}{Fore.CYAN}        ║
  ║  {Fore.RED}Likes       {Fore.WHITE}{stats.get('total_likes', 0):<12} {Fore.GREEN}{daily.get('likes', 0):<8}{Fore.CYAN}        ║
  ║  {Fore.GREEN}Follows     {Fore.WHITE}{stats.get('total_follows', 0):<12} {Fore.GREEN}{daily.get('follows', 0):<8}{Fore.CYAN}        ║
  ║  {Fore.YELLOW}Sessions    {Fore.WHITE}{stats.get('sessions_completed', 0):<12} {Fore.GREEN}{daily.get('sessions', 0):<8}{Fore.CYAN}        ║
  ╠══════════════════════════════════════════════════╣
  ║  {Fore.WHITE}First Run: {stats.get('first_run', 'N/A')[:10]}{Fore.CYAN}                         ║
  ║  {Fore.WHITE}Last Run:  {(stats.get('last_run') or 'Never')[:10]}{Fore.CYAN}                         ║
  ╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def show_menu():
    """Display interactive menu."""
    if HAS_RICH:
        menu_table = Table(show_header=False, box=box.ROUNDED, border_style="cyan", padding=(0, 2))
        menu_table.add_column("Option", style="bold yellow", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1", "Run ALL bots (views + likes + follows)")
        menu_table.add_row("2", "Run on auto-schedule (every 30 min)")
        menu_table.add_row("3", "Run View Bot only")
        menu_table.add_row("4", "Run Like/Engagement Bot only")
        menu_table.add_row("5", "Run Follower Bot only")
        menu_table.add_row("6", "Refresh US Proxies")
        menu_table.add_row("7", "Show Statistics")
        menu_table.add_row("8", "Test Setup")
        menu_table.add_row("0", "Exit")

        console.print(Panel(menu_table, title="[bold cyan]Menu[/]", border_style="cyan"))
        choice = console.input("\n  [bold yellow]Select option:[/] ")
        return choice.strip()
    else:
        print(f"""
{Fore.CYAN}  ┌─── Menu ────────────────────────────────────────┐
  │  {Fore.YELLOW}[1]{Fore.WHITE} Run ALL bots (views + likes + follows)      {Fore.CYAN}│
  │  {Fore.YELLOW}[2]{Fore.WHITE} Run on auto-schedule (every 30 min)        {Fore.CYAN}│
  │  {Fore.YELLOW}[3]{Fore.WHITE} Run View Bot only                          {Fore.CYAN}│
  │  {Fore.YELLOW}[4]{Fore.WHITE} Run Like/Engagement Bot only               {Fore.CYAN}│
  │  {Fore.YELLOW}[5]{Fore.WHITE} Run Follower Bot only                      {Fore.CYAN}│
  │  {Fore.YELLOW}[6]{Fore.WHITE} Refresh US Proxies                         {Fore.CYAN}│
  │  {Fore.YELLOW}[7]{Fore.WHITE} Show Statistics                            {Fore.CYAN}│
  │  {Fore.YELLOW}[8]{Fore.WHITE} Test Setup                                 {Fore.CYAN}│
  │  {Fore.YELLOW}[0]{Fore.WHITE} Exit                                       {Fore.CYAN}│
  └──────────────────────────────────────────────────┘{Style.RESET_ALL}
""")
        choice = input(f"  {Fore.YELLOW}Select option: {Style.RESET_ALL}")
        return choice.strip()


def show_proxy_rotation(old_proxy: str, new_proxy: str):
    """Display proxy rotation event."""
    if HAS_RICH:
        console.print(
            f"  [yellow]↻ Rotating proxy:[/] "
            f"[dim]{old_proxy[:25]}...[/] → [bold cyan]{new_proxy[:25]}...[/]"
        )
    else:
        print(f"  {Fore.YELLOW}↻ Rotating: {Fore.WHITE}{old_proxy[:25]}... → {Fore.CYAN}{new_proxy[:25]}...{Style.RESET_ALL}")


def show_error(message: str):
    """Display error message."""
    if HAS_RICH:
        console.print(Panel(f"[bold red]{message}[/]", border_style="red", title="[red]Error[/]"))
    else:
        print(f"\n{Fore.RED}  ╔═══ ERROR ═══════════════════════════════════════╗")
        print(f"  ║  {message[:50]}")
        print(f"  ╚══════════════════════════════════════════════════╝{Style.RESET_ALL}\n")


def show_divider(char="─", style="dim"):
    """Print a divider line."""
    if HAS_RICH:
        console.print(f"  [{style}]{char * 50}[/]")
    else:
        print(f"  {Fore.WHITE}{char * 50}{Style.RESET_ALL}")
