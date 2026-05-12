"""
Caption & Hashtag Optimizer Module
=====================================
Generates optimized captions, hooks, and hashtags for the Mini Building
Construction niche. Uses trending patterns, engagement formulas, and
optional AI enhancement.

Features:
- Viral hook formulas (curiosity gap, challenge, POV, etc.)
- Niche-optimized hashtag sets (mix of big + medium + small tags)
- Caption structures proven for high engagement
- AI-enhanced captions (with OpenAI/Gemini)
- A/B testing variants
- Posting time recommendations

Usage:
    from caption_optimizer import CaptionOptimizer
    co = CaptionOptimizer()
    result = co.generate_full_caption(topic="mini house build")
"""

import random
import json
import os
from datetime import datetime
from config import Config

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
        console.print(f"  [yellow][CAPTION][/] {msg}")
    else:
        print(f"  [CAPTION] {msg}")


# ═══════════════════════════════════════════════════════════
# Hook Formulas (proven engagement patterns)
# ═══════════════════════════════════════════════════════════

HOOK_FORMULAS = {
    "curiosity_gap": [
        "You won't believe what happens at the end...",
        "Wait for the final reveal 😮",
        "Nobody expected this to actually work",
        "I didn't think this was possible until...",
        "The ending will blow your mind",
    ],
    "challenge": [
        "Can I build a mini {topic} in under 60 seconds?",
        "Building the world's smallest {topic} - challenge accepted",
        "100 bricks. 1 hour. Let's see what happens",
        "I tried building a {topic} with just my hands",
        "24 hour mini {topic} challenge",
    ],
    "pov": [
        "POV: You're a miniature construction worker",
        "POV: You shrunk down to build your dream {topic}",
        "POV: Your client wants a mini {topic} by tomorrow",
        "POV: You're building the world's tiniest {topic}",
    ],
    "satisfying": [
        "The most satisfying mini build you'll see today",
        "This is oddly satisfying to watch 🧱",
        "I could watch this all day",
        "Satisfying mini {topic} construction ASMR",
        "Warning: extremely satisfying content ahead",
    ],
    "educational": [
        "How to build a mini {topic} step by step",
        "Mini {topic} tutorial for beginners",
        "The secret technique behind mini {topic} builds",
        "3 tips for better miniature {topic} construction",
        "Learn mini building in 60 seconds",
    ],
    "series": [
        "Day {day} of building a mini city 🏗️",
        "Part {part} of the mini {topic} build",
        "Mini {topic} series - Episode {part}",
        "Building a {topic} brick by brick - Day {day}",
    ],
    "controversy": [
        "Why nobody talks about this building technique",
        "This mini build method is way too easy",
        "Am I the only one who does this?",
        "Unpopular opinion: {topic} builds are underrated",
    ],
}

# ═══════════════════════════════════════════════════════════
# Hashtag Strategy (tiered: big + medium + niche)
# ═══════════════════════════════════════════════════════════

HASHTAGS = {
    "mega": [  # 100M+ views - for reach
        "#fyp", "#foryou", "#foryoupage", "#viral", "#trending",
        "#explore", "#satisfying", "#oddlysatisfying", "#asmr",
    ],
    "large": [  # 10M-100M views - for discovery
        "#diy", "#construction", "#building", "#handmade", "#craft",
        "#timelapse", "#howto", "#tutorial", "#creative", "#art",
    ],
    "medium": [  # 1M-10M views - for niche reach
        "#minibuilding", "#miniconstruction", "#miniature", "#tinyhouse",
        "#cementcraft", "#bricklaying", "#miniworld", "#scalemodel",
        "#constructionlife", "#buildwithme", "#miniatureart",
    ],
    "small": [  # Under 1M - for niche dominance
        "#minibricks", "#minicement", "#tinybuilding", "#miniarchitecture",
        "#miniaturehouse", "#microbuilding", "#smallscale",
        "#miniDIY", "#minihomedecor", "#tinyconstruction",
        "#miniaturebuilding", "#cementart", "#minibuild",
    ],
    "trending_sounds": [  # Pair with trending audio
        "#satisfyingvideo", "#relaxing", "#chill", "#cleaningasmr",
        "#processvideo", "#makingof", "#behindthescenes",
    ],
}

# ═══════════════════════════════════════════════════════════
# Caption Structures
# ═══════════════════════════════════════════════════════════

CAPTION_STRUCTURES = [
    # Hook + CTA
    "{hook}\n\n{cta}\n\n{hashtags}",
    # Hook + Detail + CTA
    "{hook}\n\n{detail}\n\n{cta}\n\n{hashtags}",
    # Short & Punchy
    "{hook} {emoji}\n{hashtags}",
    # Question + Hook
    "{question}\n\n{hook}\n\n{hashtags}",
    # Series format
    "{hook}\n\n{detail}\n\nFollow for Part {part}! {emoji}\n\n{hashtags}",
]

CTA_OPTIONS = [
    "Follow for more mini builds! 🔨",
    "Like if you want Part 2! ❤️",
    "Comment what I should build next! 👇",
    "Save this for later 🔖",
    "Share with someone who loves building! 📤",
    "Follow for daily mini construction content 🧱",
    "Double tap if this was satisfying! ❤️",
    "Turn on notifications for the next build! 🔔",
    "Which part was your favorite? Comment below! 💬",
    "Tag someone who needs to see this! 👀",
]

EMOJIS = ["🧱", "🏗️", "🔨", "🏠", "✨", "😮", "🔥", "💪", "⚡", "🎯", "👀", "🤯"]

QUESTIONS = [
    "Would you live in this tiny house?",
    "How long do you think this took?",
    "Can you guess what I'm building?",
    "Would you try this at home?",
    "Rate this build 1-10!",
    "Which is harder: big or mini construction?",
    "Should I add a pool to this mini house?",
]

# ═══════════════════════════════════════════════════════════
# Optimal Posting Times (by day of week, UTC)
# ═══════════════════════════════════════════════════════════

BEST_POSTING_TIMES = {
    "monday": ["07:00", "12:00", "19:00"],
    "tuesday": ["08:00", "13:00", "18:00"],
    "wednesday": ["07:00", "11:00", "19:00"],
    "thursday": ["09:00", "12:00", "20:00"],
    "friday": ["08:00", "14:00", "21:00"],
    "saturday": ["10:00", "14:00", "20:00"],
    "sunday": ["09:00", "13:00", "19:00"],
}


class CaptionOptimizer:
    """Generates optimized captions and hashtags for mini building content."""

    def __init__(self):
        self.ai_available = bool(Config.OPENAI_API_KEY or Config.GEMINI_API_KEY)

    def generate_hook(self, topic: str = "house", style: str = None) -> str:
        """
        Generate a viral hook.

        Args:
            topic: Building topic (e.g., "house", "bridge", "pool")
            style: Hook style (curiosity_gap, challenge, pov, satisfying, educational, series)

        Returns:
            Hook text string
        """
        if style is None:
            style = random.choice(list(HOOK_FORMULAS.keys()))

        hooks = HOOK_FORMULAS.get(style, HOOK_FORMULAS["curiosity_gap"])
        hook = random.choice(hooks)

        return hook.format(
            topic=topic,
            day=random.randint(1, 365),
            part=random.randint(2, 10),
        )

    def generate_hashtags(self, count: int = 15, strategy: str = "balanced") -> list:
        """
        Generate an optimized hashtag set.

        Args:
            count: Total number of hashtags (recommended 15-20)
            strategy: "balanced" (mix all), "reach" (more mega/large), "niche" (more small/medium)

        Returns:
            List of hashtag strings
        """
        tags = set()

        if strategy == "reach":
            # Focus on discovery
            distribution = {"mega": 4, "large": 4, "medium": 4, "small": 2, "trending_sounds": 1}
        elif strategy == "niche":
            # Focus on niche dominance
            distribution = {"mega": 2, "large": 2, "medium": 5, "small": 5, "trending_sounds": 1}
        else:
            # Balanced
            distribution = {"mega": 3, "large": 3, "medium": 4, "small": 4, "trending_sounds": 1}

        for tier, num in distribution.items():
            available = HASHTAGS.get(tier, [])
            sample_size = min(num, len(available))
            tags.update(random.sample(available, sample_size))

        # Ensure we hit the target count
        all_tags = []
        for tier_tags in HASHTAGS.values():
            all_tags.extend(tier_tags)

        while len(tags) < count:
            tags.add(random.choice(all_tags))

        return list(tags)[:count]

    def generate_caption(self, topic: str = "house", hook: str = None,
                         include_cta: bool = True, hashtag_count: int = 15) -> str:
        """
        Generate a complete optimized caption.

        Args:
            topic: Build topic
            hook: Custom hook (auto-generated if None)
            include_cta: Whether to include call-to-action
            hashtag_count: Number of hashtags

        Returns:
            Full caption string ready to paste
        """
        if hook is None:
            hook = self.generate_hook(topic)

        hashtags = self.generate_hashtags(hashtag_count)
        hashtag_str = " ".join(hashtags)
        cta = random.choice(CTA_OPTIONS) if include_cta else ""
        emoji = random.choice(EMOJIS)
        question = random.choice(QUESTIONS)
        detail = f"Building a miniature {topic} from scratch with cement and mini bricks"
        part = random.randint(2, 10)

        structure = random.choice(CAPTION_STRUCTURES)
        caption = structure.format(
            hook=hook,
            cta=cta,
            hashtags=hashtag_str,
            emoji=emoji,
            question=question,
            detail=detail,
            part=part,
        )

        return caption.strip()

    def generate_title(self, topic: str = "house") -> str:
        """Generate an optimized video title."""
        titles = [
            f"Mini {topic.title()} Build From Scratch 🧱 #Shorts",
            f"Building a Tiny {topic.title()} With Cement ✨ #Shorts",
            f"Satisfying Mini {topic.title()} Construction 🏗️ #Shorts",
            f"Watch Me Build a Miniature {topic.title()} 😮 #Shorts",
            f"Mini {topic.title()} Tutorial - Step by Step 🔨 #Shorts",
            f"The Most Satisfying Mini {topic.title()} Build #Shorts",
            f"Day {{}} of Building a Mini City 🏙️ #Shorts".format(random.randint(1, 100)),
            f"POV: Mini {topic.title()} Construction Worker 👷 #Shorts",
            f"Tiny {topic.title()} Challenge - Can I Do It? 🎯 #Shorts",
            f"Mini {topic.title()} ASMR Build 🎧 #Shorts",
        ]
        return random.choice(titles)

    def generate_full_caption(self, topic: str = "house", style: str = None,
                              strategy: str = "balanced") -> dict:
        """
        Generate a complete caption package (title + description + hashtags + hook).

        Args:
            topic: Building topic
            style: Hook style
            strategy: Hashtag strategy

        Returns:
            Dict with title, description, hashtags, hook, cta, posting_time
        """
        hook = self.generate_hook(topic, style)
        hashtags = self.generate_hashtags(strategy=strategy)
        title = self.generate_title(topic)
        caption = self.generate_caption(topic, hook)
        cta = random.choice(CTA_OPTIONS)
        posting_time = self.get_best_posting_time()

        result = {
            "title": title,
            "hook": hook,
            "caption": caption,
            "hashtags": hashtags,
            "cta": cta,
            "topic": topic,
            "style": style or "mixed",
            "posting_time": posting_time,
            "generated_at": datetime.now().isoformat(),
        }

        # Enhance with AI if available
        if self.ai_available:
            result = self._enhance_with_ai(result)

        return result

    def _enhance_with_ai(self, caption_data: dict) -> dict:
        """Use AI to improve the caption."""
        try:
            prompt = f"""Improve this TikTok/YouTube Shorts caption for the mini building construction niche.
Keep it short, viral, and engaging. Return only the improved caption text.

Current hook: {caption_data['hook']}
Current caption: {caption_data['caption'][:200]}
Topic: {caption_data['topic']}

Make the hook more attention-grabbing and the CTA more compelling. Keep it under 150 characters for the main text (before hashtags)."""

            if Config.OPENAI_API_KEY:
                import openai
                client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.9,
                )
                enhanced = response.choices[0].message.content.strip()
                caption_data["ai_enhanced_caption"] = enhanced
                caption_data["ai_model"] = "gpt-4o-mini"

            elif Config.GEMINI_API_KEY:
                import google.generativeai as genai
                genai.configure(api_key=Config.GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                enhanced = response.text.strip()
                caption_data["ai_enhanced_caption"] = enhanced
                caption_data["ai_model"] = "gemini-1.5-flash"

        except Exception as e:
            caption_data["ai_error"] = str(e)

        return caption_data

    def get_best_posting_time(self) -> str:
        """Get the best posting time for today."""
        today = datetime.now().strftime("%A").lower()
        times = BEST_POSTING_TIMES.get(today, ["12:00", "18:00"])
        return random.choice(times)

    def generate_ab_variants(self, topic: str = "house", count: int = 3) -> list:
        """
        Generate A/B testing variants of captions.

        Args:
            topic: Building topic
            count: Number of variants

        Returns:
            List of caption dicts
        """
        variants = []
        styles = list(HOOK_FORMULAS.keys())
        strategies = ["balanced", "reach", "niche"]

        for i in range(count):
            style = styles[i % len(styles)]
            strategy = strategies[i % len(strategies)]
            variant = self.generate_full_caption(topic, style=style, strategy=strategy)
            variant["variant"] = chr(65 + i)  # A, B, C...
            variants.append(variant)

        return variants

    def display_caption(self, caption_data: dict):
        """Display a generated caption beautifully."""
        if HAS_RICH:
            console.print(Panel(
                f"[bold cyan]{caption_data.get('title', '')}[/]",
                border_style="cyan",
                title=f"[bold]Variant {caption_data.get('variant', '')}[/]" if caption_data.get('variant') else "[bold]Caption[/]",
            ))

            console.print(f"  [bold yellow]Hook:[/] {caption_data.get('hook', '')}")
            console.print(f"  [bold green]CTA:[/] {caption_data.get('cta', '')}")
            console.print(f"  [bold]Post at:[/] {caption_data.get('posting_time', '')} UTC")

            if caption_data.get("ai_enhanced_caption"):
                console.print(f"\n  [bold magenta]AI Enhanced:[/] {caption_data['ai_enhanced_caption']}")

            # Caption preview
            console.print(f"\n  [dim]─── Full Caption ───[/]")
            console.print(f"  {caption_data.get('caption', '')[:300]}")

            # Hashtags
            tags = caption_data.get("hashtags", [])
            if tags:
                console.print(f"\n  [bold]Hashtags ({len(tags)}):[/] [dim]{' '.join(tags[:10])}...[/]")
            console.print()
        else:
            print(f"\n  Title: {caption_data.get('title', '')}")
            print(f"  Hook: {caption_data.get('hook', '')}")
            print(f"  CTA: {caption_data.get('cta', '')}")
            print(f"  Post at: {caption_data.get('posting_time', '')} UTC")
            print(f"  Hashtags: {len(caption_data.get('hashtags', []))}")
            print(f"  Caption: {caption_data.get('caption', '')[:200]}...")
            print()

    def save_captions(self, captions: list, filename: str = None) -> str:
        """Save generated captions to JSON."""
        Config.ensure_dirs()
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(Config.OUTPUT_DIR, f"captions_{timestamp}.json")

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(captions, f, indent=2, ensure_ascii=False)

        _log(f"Saved {len(captions)} captions to: {filename}")
        return filename


# ═══════════════════════════════════════════════════════════
# Standalone usage
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    co = CaptionOptimizer()

    print("\n  Caption & Hashtag Optimizer - Mini Building Construction")
    print("  " + "=" * 58)
    print(f"  AI available: {'Yes' if co.ai_available else 'No (using templates)'}")

    # Generate A/B variants
    print("\n  Generating 3 caption variants for 'swimming pool' build...\n")
    variants = co.generate_ab_variants("swimming pool", count=3)

    for v in variants:
        co.display_caption(v)

    # Save
    filepath = co.save_captions(variants)
    print(f"  Saved to: {filepath}")

    # Show best posting times
    print(f"\n  Best posting time today: {co.get_best_posting_time()} UTC")
