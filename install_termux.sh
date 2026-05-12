#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# TikTok Bot - Termux Installation Script (Android)
# ============================================================
# Run this ONCE to set up everything on your Android phone.
#
# Usage:
#   pkg install git -y
#   git clone https://github.com/salman09bhutta/TikTok-Bot-.git
#   cd TikTok-Bot-
#   bash install_termux.sh
# ============================================================

echo ""
echo "======================================================"
echo "  TikTok Bot - Termux Installer (Android)"
echo "  Target: @xxmr.building"
echo "======================================================"
echo ""

# Update packages
echo "[1/7] Updating Termux packages..."
pkg update -y && pkg upgrade -y
echo "       Done."
echo ""

# Install required system packages
echo "[2/7] Installing system dependencies..."
pkg install -y python python-pip git chromium wget proot resolv-conf
echo "       Done."
echo ""

# Install Python dependencies
echo "[3/7] Installing Python packages..."
pip install --upgrade pip setuptools
pip install selenium requests python-dotenv \
    fake-useragent schedule colorama pysocks aiohttp aiohttp-socks \
    rich pyfiglet tabulate
echo "       Done."
echo ""

# Install chromedriver for Termux
echo "[4/7] Setting up Chromium + ChromeDriver..."
pkg install -y chromium
# Termux chromium package includes chromedriver
which chromedriver >/dev/null 2>&1 || pkg install -y chromium
echo "       Chromium: $(chromium --version 2>/dev/null || echo 'installed')"
echo "       Done."
echo ""

# Setup .env file
echo "[5/7] Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    # Update for Termux/Android paths
    sed -i 's|CHROME_BINARY_PATH=.*|CHROME_BINARY_PATH=/data/data/com.termux/files/usr/bin/chromium-browser|' .env
    sed -i 's|TIKTOK_TARGET_USERNAME=.*|TIKTOK_TARGET_USERNAME=xxmr.building|' .env
    echo "       Created .env with Termux settings."
else
    echo "       .env already exists."
fi
echo ""

# Scrape fresh US proxies
echo "[6/7] Fetching fresh US proxies..."
python proxy_scraper.py --update-env
echo "       Done."
echo ""

# Create Termux launcher script
echo "[7/7] Creating launcher script..."
cat > run_bot.sh << 'LAUNCHER'
#!/data/data/com.termux/files/usr/bin/bash
# TikTok Bot - Termux Launcher

echo ""
echo "======================================================"
echo "  TikTok Bot - @xxmr.building"
echo "  US Views | Followers | Likes | Engagement"
echo "======================================================"
echo ""
echo "  [1] Run ALL bots once"
echo "  [2] Run on schedule (auto-repeat every 30 min)"
echo "  [3] Views only"
echo "  [4] Likes only"
echo "  [5] Follows only"
echo "  [6] Refresh US Proxies"
echo "  [7] Show Stats"
echo "  [8] Test Setup"
echo "  [0] Exit"
echo ""
read -p "  Select (0-8): " choice

case $choice in
    1) python main.py --once ;;
    2) python main.py ;;
    3) python main.py --views ;;
    4) python main.py --likes ;;
    5) python main.py --follows ;;
    6) python proxy_scraper.py --test --update-env ;;
    7) python main.py --stats ;;
    8) python test_setup.py ;;
    0) exit 0 ;;
    *) echo "Invalid choice" ;;
esac
LAUNCHER

chmod +x run_bot.sh
echo "       Done."
echo ""

echo "======================================================"
echo "  INSTALLATION COMPLETE!"
echo "======================================================"
echo ""
echo "  To run the bot:"
echo "    bash run_bot.sh"
echo ""
echo "  Or directly:"
echo "    python main.py --once"
echo ""
echo "  Username: @xxmr.building"
echo "  Proxies:  $(wc -l < us_proxies.txt 2>/dev/null || echo '0') US proxies loaded"
echo ""
echo "  TIP: To run in background:"
echo "    nohup python main.py > output.log 2>&1 &"
echo ""
