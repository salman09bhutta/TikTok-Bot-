"""
Content Idea Generator Module
================================
Generates viral video scripts, hooks, and concepts for the
Mini Building Construction niche using AI or built-in templates.

Works with:
- OpenAI GPT (if API key provided)
- Google Gemini (if API key provided)
- Built-in templates (no API needed - offline mode)
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


# ═══════════════════════════════════════════════════════════
# Built-in Templates (works without any AI API)
# ═══════════════════════════════════════════════════════════

HOOKS = [
    "Watch me build a tiny house with just cement and a spoon",
    "This mini construction took 72 hours straight",
    "POV: You're a miniature construction worker",
    "I built the world's smallest working bridge",
    "Day {day} of building a mini city from scratch",
    "You won't believe what I built with toothpicks and cement",
    "This mini building technique is 1000 years old",
    "Satisfying mini bricklaying you can't stop watching",
    "Building a mini swimming pool that actually holds water",
    "Turning a pile of sand into a miniature mansion",
    "Can I build a tiny house in under 60 seconds?",
    "The most satisfying mini construction video ever",
    "I spent 100 hours on this tiny masterpiece",
    "Mini building hack that actually works",
    "Watch this cement dry in the most satisfying way",
    "Building a miniature {building} step by step",
    "This tiny {building} is fully functional",
    "Mini construction ASMR that hits different",
    "How to build a mini {building} with household items",
    "The detail in this miniature {building} is insane",
]

BUILDINGS = [
    "house", "castle", "bridge", "swimming pool", "skyscraper",
    "cottage", "mansion", "apartment building", "temple", "fountain",
    "garden", "fireplace", "oven", "waterfall", "staircase",
    "underground bunker", "treehouse", "garage", "barn", "church",
    "pyramid", "tower", "well", "brick wall", "archway",
]

SCRIPTS = [
    {
        "title": "Mini House Build from Scratch",
        "hook": "Watch me build a tiny house with nothing but cement and my hands",
        "scenes": [
            "Show raw materials (cement, sand, mini bricks, water)",
            "Mix cement with satisfying ASMR sounds",
            "Lay the foundation with tiny trowel",
            "Build walls brick by brick (timelapse)",
            "Add roof structure and tiles",
            "Final reveal with mini furniture inside",
        ],
        "duration": "45-60 seconds",
        "style": "timelapse with close-ups",
    },
    {
        "title": "Satisfying Bricklaying ASMR",
        "hook": "The most satisfying mini bricklaying video on the internet",
        "scenes": [
            "Close-up of mixing mortar",
            "Placing tiny bricks one by one (ASMR tapping)",
            "Smoothing cement between bricks",
            "Building up wall layer by layer",
            "Reveal perfect miniature wall",
        ],
        "duration": "30-45 seconds",
        "style": "close-up ASMR, no music, natural sounds only",
    },
    {
        "title": "Mini Swimming Pool Build",
        "hook": "Building a mini swimming pool that actually holds water",
        "scenes": [
            "Dig tiny hole in ground/container",
            "Line with cement mixture",
            "Build tile walls around edge",
            "Add drainage and steps",
            "Fill with water - reveal moment",
            "Add tiny pool furniture",
        ],
        "duration": "50-60 seconds",
        "style": "POV top-down, satisfying transitions",
    },
    {
        "title": "Cement Craft Castle",
        "hook": "I turned $2 of cement into a medieval castle",
        "scenes": [
            "Show just cement bag and tools",
            "Pour and shape base foundation",
            "Carve castle walls and towers",
            "Add battlements and details",
            "Paint/seal the finished castle",
            "Final cinematic reveal shot",
        ],
        "duration": "45-55 seconds",
        "style": "overhead angles, dramatic reveal",
    },
    {
        "title": "100 Mini Bricks Challenge",
        "hook": "Can I build something amazing with exactly 100 mini bricks?",
        "scenes": [
            "Count out exactly 100 bricks",
            "Plan the design (quick sketch)",
            "Start building foundation",
            "Timelapse middle section",
            "Running low on bricks - tension",
            "Final brick placed - perfect fit reveal",
        ],
        "duration": "55-60 seconds",
        "style": "challenge format, countdown overlay",
    },
]

CAPTIONS_TEMPLATES = [
    "Day {day} of mini building 🧱 #minibuilding #construction #satisfying",
    "Building a tiny {building} from scratch 🏗️ #miniconstruction #diy #asmr",
    "This took {hours} hours but worth every second ✨ #miniature #build #viral",
    "Mini {building} tutorial 🔨 Would you try this? #tinyhouse #craft #howto",
    "The most satisfying build yet 😮 #satisfying #construction #minibuilding",
    "Guess what I'm building... 🤔 #minibuilding #construction #guessthebuild",
    "Mini construction hits different at 3am 🌙 #latenight #building #asmr",
    "Reply with what I should build next! 👇 #minibuilding #diy #challenge",
]

TRENDING_HASHTAGS = [
    "#minibuilding", "#miniconstruction", "#satisfying", "#asmr",
    "#tinyhouse", "#diy", "#construction", "#cement", "#miniature",
    "#bricklaying", "#oddlysatisfying", "#handmade", "#craft",
    "#buildingprocess", "#timelapse", "#miniworld", "#trending",
    "#viral", "#fyp", "#foryou", "#foryoupage", "#explore",
    "#constructionlife", "#minibricks", "#cementcraft",
    "#woodworking", "#architecture", "#miniarchitecture",
    "#satisfyingvideos", "#buildwithme",
]


class IdeaGenerator:
    """Generates content ideas for Mini Building Construction niche."""

    def __init__(self):
        self.ai_available = bool(Config.OPENAI_API_KEY or Config.GEMINI_API_KEY)
        self.ideas_generated = 0

    def generate_hook(self) -> str:
        """Generate a single viral hook."""
        hook = random.choice(HOOKS)
        building = random.choice(BUILDINGS)
        day = random.randint(1, 365)
        return hook.format(building=building, day=day)

    def generate_script(self) -> dict:
        """Generate a complete video script."""
        if self.ai_available:
            return self._generate_ai_script()
        return self._generate_template_script()

    def _generate_template_script(self) -> dict:
        """Generate script from built-in templates."""
        base_script = random.choice(SCRIPTS).copy()
        base_script["hook"] = self.generate_hook()
        base_script["generated_at"] = datetime.now().isoformat()
        base_script["hashtags"] = self._pick_hashtags()
        base_script["caption"] = self._generate_caption()
        self.ideas_generated += 1
        return base_script

    def _generate_ai_script(self) -> dict:
        """Generate script using AI API."""
        prompt = f"""Generate a viral TikTok/YouTube Shorts video script for the "Mini Building Construction" niche.

The video should be 45-60 seconds, vertical format (9:16).

Return a JSON object with:
- "title": catchy title
- "hook": opening hook (first 3 seconds, must grab attention)
- "scenes": list of 5-7 scene descriptions
- "duration": recommended duration
- "style": visual style description
- "caption": social media caption with emojis
- "hashtags": list of 8-12 relevant hashtags

Focus on: miniature building, cement crafts, tiny construction, satisfying content, ASMR elements.
Make it trendy and viral-worthy."""

        try:
            if Config.OPENAI_API_KEY:
                return self._call_openai(prompt)
            elif Config.GEMINI_API_KEY:
                return self._call_gemini(prompt)
        except Exception as e:
            print(f"  AI generation failed ({e}), using templates...")
            return self._generate_template_script()

    def _call_openai(self, prompt: str) -> dict:
        """Call OpenAI GPT API."""
        import openai
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a viral content strategist for mini building construction TikTok/Shorts. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.9,
        )

        script = json.loads(response.choices[0].message.content)
        script["generated_at"] = datetime.now().isoformat()
        script["ai_model"] = "gpt-4o-mini"
        self.ideas_generated += 1
        return script

    def _call_gemini(self, prompt: str) -> dict:
        """Call Google Gemini API."""
        import google.generativeai as genai
        genai.configure(api_key=Config.GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"{prompt}\n\nRespond with valid JSON only, no markdown.",
            generation_config={"temperature": 0.9},
        )

        # Clean response
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]

        script = json.loads(text)
        script["generated_at"] = datetime.now().isoformat()
        script["ai_model"] = "gemini-1.5-flash"
        self.ideas_generated += 1
        return script

    def _pick_hashtags(self, count: int = 10) -> list:
        """Pick random trending hashtags."""
        return random.sample(TRENDING_HASHTAGS, min(count, len(TRENDING_HASHTAGS)))

    def _generate_caption(self) -> str:
        """Generate a social media caption."""
        template = random.choice(CAPTIONS_TEMPLATES)
        return template.format(
            building=random.choice(BUILDINGS),
            day=random.randint(1, 365),
            hours=random.randint(2, 100),
        )

    def generate_batch(self, count: int = 5) -> list:
        """Generate multiple content ideas."""
        ideas = []
        for _ in range(count):
            ideas.append(self.generate_script())
        return ideas

    def save_ideas(self, ideas: list, filename: str = None) -> str:
        """Save generated ideas to JSON file."""
        Config.ensure_dirs()
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(Config.OUTPUT_DIR, f"ideas_{timestamp}.json")

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(ideas, f, indent=2, ensure_ascii=False)

        return filename

    def display_idea(self, idea: dict):
        """Display a generated idea beautifully."""
        if HAS_RICH:
            # Title panel
            console.print(Panel(
                f"[bold cyan]{idea.get('title', 'Untitled')}[/]",
                border_style="cyan",
                title="[bold]Video Concept[/]",
            ))

            # Hook
            console.print(f"  [bold yellow]Hook:[/] {idea.get('hook', '')}\n")

            # Scenes table
            table = Table(box=box.SIMPLE, border_style="dim")
            table.add_column("#", style="bold", width=3)
            table.add_column("Scene", style="white")

            for i, scene in enumerate(idea.get("scenes", []), 1):
                table.add_row(str(i), scene)

            console.print(table)

            # Details
            console.print(f"\n  [bold]Duration:[/] {idea.get('duration', '45-60s')}")
            console.print(f"  [bold]Style:[/] {idea.get('style', 'standard')}")
            console.print(f"  [bold]Caption:[/] {idea.get('caption', '')}")

            # Hashtags
            tags = idea.get("hashtags", [])
            if tags:
                tag_str = " ".join(tags) if isinstance(tags[0], str) and tags[0].startswith("#") else " ".join(f"#{t}" for t in tags)
                console.print(f"  [bold]Tags:[/] [dim]{tag_str}[/]")

            console.print()
        else:
            print(f"\n{'='*60}")
            print(f"  Title: {idea.get('title', 'Untitled')}")
            print(f"  Hook: {idea.get('hook', '')}")
            print(f"  Scenes:")
            for i, scene in enumerate(idea.get("scenes", []), 1):
                print(f"    {i}. {scene}")
            print(f"  Duration: {idea.get('duration', '45-60s')}")
            print(f"  Caption: {idea.get('caption', '')}")
            print(f"{'='*60}\n")


# ═══════════════════════════════════════════════════════════
# Standalone usage
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    gen = IdeaGenerator()
    print("\n  Generating 3 content ideas...\n")

    ideas = gen.generate_batch(3)
    for idea in ideas:
        gen.display_idea(idea)

    # Save to file
    filepath = gen.save_ideas(ideas)
    print(f"  Saved to: {filepath}")
