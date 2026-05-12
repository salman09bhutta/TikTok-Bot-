# TikTok Bot - US Views, Followers, Likes & Engagement

Automated TikTok bot that generates **United States-based** views, followers, likes, and engagement for your target account. Uses undetected Chrome browsers with US proxies to simulate real organic traffic.

## Features

- **US Views** - Watches your videos from US-based IPs with realistic watch times
- **US Followers** - Follows your account from US geolocated sessions
- **US Likes** - Likes your videos with human-like interaction patterns
- **Engagement Boost** - Full engagement flow (watch + like + share hover)
- **Anti-Detection** - Undetected Chrome, random user agents, human-like delays
- **Proxy Rotation** - Rotates through US proxies to avoid IP bans
- **US Geolocation** - Sets browser timezone, locale, and GPS to US (New York)
- **Scheduling** - Runs automatically on a configurable schedule
- **Statistics** - Tracks all-time and daily performance metrics

## Project Structure

```
TikTok-Bot-/
├── main.py              # Entry point - CLI & scheduler
├── config.py            # Configuration from .env
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment config
├── .gitignore
├── bot/
│   ├── __init__.py
│   ├── viewer.py        # View generation bot
│   ├── engager.py       # Like & engagement bot
│   ├── follower.py      # Follower generation bot
│   └── stats.py         # Performance tracking
├── browser/
│   ├── __init__.py
│   └── driver.py        # Chrome driver setup with US proxy
└── utils/
    ├── __init__.py
    ├── logger.py         # Colored logging
    └── helpers.py        # Delay & randomization utilities
```

## Prerequisites

- Python 3.9+
- Google Chrome browser installed
- US-based proxy service (SOCKS5 or HTTP proxies)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/salman09bhutta/TikTok-Bot-.git
   cd TikTok-Bot-
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your settings (see Configuration section below).

## Configuration

Edit the `.env` file with your settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `TIKTOK_TARGET_USERNAME` | Target TikTok username (without @) | *required* |
| `PROXY_LIST` | Comma-separated US proxy URLs | *required* |
| `MAX_VIEWS_PER_SESSION` | Views to generate per session | 50 |
| `MAX_LIKES_PER_SESSION` | Likes to give per session | 20 |
| `MAX_FOLLOWS_PER_SESSION` | Follows per session | 10 |
| `WATCH_TIME_MIN_SECONDS` | Minimum video watch time | 15 |
| `WATCH_TIME_MAX_SECONDS` | Maximum video watch time | 60 |
| `MIN_ACTION_DELAY` | Min delay between actions (sec) | 3 |
| `MAX_ACTION_DELAY` | Max delay between actions (sec) | 10 |
| `SESSION_COOLDOWN_MINUTES` | Minutes between scheduled runs | 30 |
| `HEADLESS` | Run browser without GUI | true |
| `LOG_LEVEL` | Logging level | INFO |

### Proxy Format

US proxies should be in this format:
```
socks5://username:password@us-host:port
http://username:password@us-host:port
```

## Usage

### Run All Bots (Scheduled Mode)
```bash
python main.py
```
Runs views, likes, and follows on a recurring schedule.

### Run All Bots Once
```bash
python main.py --once
```

### Run Individual Bots
```bash
python main.py --views      # Only generate views
python main.py --likes      # Only generate likes
python main.py --follows    # Only generate followers
```

### View Statistics
```bash
python main.py --stats
```

## How It Works

1. **Browser Launch** - Creates an undetected Chrome instance with a random US proxy
2. **US Geolocation** - Sets timezone to `America/New_York`, locale to `en-US`, GPS to NYC
3. **Profile Navigation** - Goes to the target account's TikTok page
4. **Video Interaction** - Watches videos with realistic durations, scrolling, and pauses
5. **Engagement** - Likes videos, follows the account with human-like click patterns
6. **Proxy Rotation** - Switches to a new US proxy every ~10 actions
7. **Cooldown** - Waits between sessions to avoid rate limiting

## Anti-Detection Features

- **Undetected ChromeDriver** - Bypasses bot detection
- **Random User Agents** - Different browser fingerprint each session
- **Human-Like Delays** - Randomized timing between all actions
- **Realistic Watch Times** - Videos watched for 15-60 seconds
- **Scroll Simulation** - Random scrolling during video playback
- **Mouse Movement** - ActionChains for natural click behavior
- **Proxy Rotation** - Fresh IP every few actions

## Important Notes

- **US Proxies Required** - This bot specifically targets US-based engagement. You need quality US residential or datacenter proxies.
- **Rate Limiting** - Keep session limits conservative to avoid account flags.
- **Proxy Quality** - Results depend heavily on proxy quality. Residential proxies work best.
- **No Guarantees** - TikTok's algorithm and detection methods change frequently.

## Disclaimer

This tool is for educational and research purposes only. Use at your own risk. Automating interactions on TikTok may violate their Terms of Service. The authors are not responsible for any account restrictions or bans.

## License

MIT License
