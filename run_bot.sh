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
