"""
US Proxy Scraper
================
Fetches fresh US proxies from multiple free public sources.
Run this before starting the bot to get the latest working US proxies.

Sources:
- proxifly/free-proxy-list (GitHub) - US-filtered proxies
- TheSpeedX/PROXY-List (GitHub) - Large proxy lists
- monosans/proxy-list (GitHub) - Verified proxies
- pubproxy.com API
- Free proxy APIs

Usage:
    python proxy_scraper.py              # Scrape and save proxies
    python proxy_scraper.py --test       # Scrape and test connectivity
    python proxy_scraper.py --update-env # Scrape and update .env file
"""

import requests
import re
import time
import argparse
import socket
import concurrent.futures
from typing import List, Set

# Free US proxy sources (updated hourly/daily)
PROXY_SOURCES = {
    # Proxifly - US-specific proxies (best source)
    "proxifly_us": "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/US/data.txt",
    # TheSpeedX - SOCKS5 proxies
    "thespeedx_socks5": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    # TheSpeedX - HTTP proxies
    "thespeedx_http": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    # monosans - SOCKS5 proxies
    "monosans_socks5": "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    # monosans - HTTP proxies
    "monosans_http": "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    # mmpx12 - HTTPS proxies
    "mmpx12_https": "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    # hookzof - SOCKS5
    "hookzof_socks5": "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
}

# Known US IP ranges (partial check for US-based proxies)
US_IP_PREFIXES = [
    "3.", "4.", "8.", "12.", "13.", "15.", "16.", "17.", "18.", "20.",
    "23.", "24.", "32.", "34.", "35.", "38.", "40.", "44.", "45.", "47.",
    "50.", "52.", "54.", "56.", "63.", "64.", "65.", "66.", "67.", "68.",
    "69.", "70.", "71.", "72.", "73.", "74.", "75.", "76.", "96.", "97.",
    "98.", "99.", "100.", "104.", "107.", "108.", "128.", "129.", "130.",
    "131.", "132.", "134.", "135.", "136.", "137.", "138.", "140.", "141.",
    "142.", "143.", "144.", "146.", "147.", "148.", "149.", "150.", "152.",
    "154.", "155.", "156.", "157.", "158.", "159.", "160.", "161.", "162.",
    "163.", "164.", "165.", "166.", "167.", "168.", "169.", "170.", "172.",
    "173.", "174.", "178.", "181.", "184.", "185.", "192.", "193.", "198.",
    "199.", "204.", "205.", "206.", "207.", "208.", "209.", "216.",
]


def fetch_proxies_from_url(url: str, source_name: str) -> Set[str]:
    """Fetch proxy list from a URL."""
    proxies = set()
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        for line in response.text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Normalize proxy format
            if "://" in line:
                proxies.add(line)
            else:
                # Determine protocol from source name
                if "socks5" in source_name:
                    proxies.add(f"socks5://{line}")
                elif "socks4" in source_name:
                    proxies.add(f"socks4://{line}")
                else:
                    proxies.add(f"http://{line}")

        print(f"  [+] {source_name}: {len(proxies)} proxies fetched")

    except Exception as e:
        print(f"  [-] {source_name}: Failed ({e})")

    return proxies


def filter_us_proxies(proxies: Set[str]) -> List[str]:
    """Filter proxies that are likely US-based by IP prefix."""
    us_proxies = []
    for proxy in proxies:
        # Extract IP from proxy URL
        match = re.search(r"://(\d+\.\d+\.\d+\.\d+)", proxy)
        if match:
            ip = match.group(1)
            # Check if IP starts with known US prefixes
            for prefix in US_IP_PREFIXES:
                if ip.startswith(prefix):
                    us_proxies.append(proxy)
                    break
    return us_proxies


def test_proxy(proxy: str, timeout: int = 5) -> bool:
    """Test if a proxy is working by attempting a connection."""
    try:
        # Extract host and port
        match = re.search(r"://([^:]+):(\d+)", proxy)
        if not match:
            return False

        host = match.group(1)
        port = int(match.group(2))

        # Quick socket test
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0

    except Exception:
        return False


def test_proxies_parallel(proxies: List[str], max_workers: int = 50) -> List[str]:
    """Test multiple proxies in parallel."""
    working = []
    total = len(proxies)

    print(f"\n  Testing {total} proxies (this may take a minute)...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {
            executor.submit(test_proxy, proxy): proxy for proxy in proxies
        }

        done_count = 0
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            done_count += 1

            if done_count % 20 == 0:
                print(f"  Progress: {done_count}/{total} tested, {len(working)} working")

            try:
                if future.result():
                    working.append(proxy)
            except Exception:
                pass

    return working


def save_proxies(proxies: List[str], filename: str = "us_proxies.txt"):
    """Save proxies to a file."""
    with open(filename, "w") as f:
        f.write("\n".join(proxies))
    print(f"\n  Saved {len(proxies)} proxies to {filename}")


def update_env_file(proxies: List[str], env_file: str = ".env"):
    """Update the .env file with the scraped proxies."""
    # Read existing .env
    try:
        with open(env_file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        # Copy from example
        try:
            with open(".env.example", "r") as f:
                content = f.read()
        except FileNotFoundError:
            content = ""

    # Format proxies for .env (comma-separated)
    proxy_string = ",".join(proxies[:100])  # Limit to 100 proxies

    # Update or add PROXY_LIST
    if "PROXY_LIST=" in content:
        content = re.sub(
            r"PROXY_LIST=.*",
            f"PROXY_LIST={proxy_string}",
            content,
        )
    else:
        content += f"\nPROXY_LIST={proxy_string}\n"

    with open(env_file, "w") as f:
        f.write(content)

    print(f"\n  Updated {env_file} with {min(len(proxies), 100)} proxies")


def scrape_all() -> List[str]:
    """Main scraping function - fetches from all sources and filters US proxies."""
    print("\n" + "=" * 60)
    print("  TikTok Bot - US Proxy Scraper")
    print("=" * 60)
    print("\n  Fetching proxies from free sources...\n")

    all_proxies = set()

    for source_name, url in PROXY_SOURCES.items():
        proxies = fetch_proxies_from_url(url, source_name)
        all_proxies.update(proxies)
        time.sleep(0.5)  # Be polite to servers

    print(f"\n  Total raw proxies: {len(all_proxies)}")

    # Filter for US proxies
    us_proxies = filter_us_proxies(all_proxies)
    print(f"  US-filtered proxies: {len(us_proxies)}")

    # Deduplicate and sort
    us_proxies = sorted(set(us_proxies))

    # Separate by protocol
    socks5 = [p for p in us_proxies if p.startswith("socks5://")]
    socks4 = [p for p in us_proxies if p.startswith("socks4://")]
    http = [p for p in us_proxies if p.startswith("http://")]

    print(f"\n  Breakdown:")
    print(f"    SOCKS5: {len(socks5)}")
    print(f"    SOCKS4: {len(socks4)}")
    print(f"    HTTP:   {len(http)}")

    # Prioritize SOCKS5 > SOCKS4 > HTTP
    prioritized = socks5 + socks4 + http
    print(f"\n  Total US proxies available: {len(prioritized)}")

    return prioritized


def main():
    parser = argparse.ArgumentParser(description="US Proxy Scraper for TikTok Bot")
    parser.add_argument(
        "--test", action="store_true", help="Test proxy connectivity"
    )
    parser.add_argument(
        "--update-env", action="store_true", help="Update .env file with proxies"
    )
    parser.add_argument(
        "--output", default="us_proxies.txt", help="Output file (default: us_proxies.txt)"
    )
    args = parser.parse_args()

    proxies = scrape_all()

    if args.test:
        proxies = test_proxies_parallel(proxies)
        print(f"\n  Working proxies after testing: {len(proxies)}")

    # Save to file
    save_proxies(proxies, args.output)

    if args.update_env:
        update_env_file(proxies)

    print("\n" + "=" * 60)
    print(f"  Done! {len(proxies)} US proxies ready to use.")
    print("=" * 60 + "\n")

    return proxies


if __name__ == "__main__":
    main()
