import json
import os
import random
import re
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
PROMPT_FILE = os.path.join(BASE_DIR, "prompts.json")


def load_prompts():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def slugify(name: str):
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)
    return name.strip('_')


class PromptLibraryNode:
    @classmethod
    def INPUT_TYPES(cls):
        prompts = load_prompts()
        names = [p["name"] for p in prompts]

        return {
            "required": {
                "mode": (["random", "select"],),
                "prompt_name": (names,),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("prompt", "negative", "cache_buster")
    FUNCTION = "run"
    CATEGORY = "Prompt Library"

    def run(self, mode, prompt_name, seed):
        prompts = load_prompts()
        # If seed < 0 we generate a fresh seed per run to avoid ComfyUI caching
        if mode == "random":
            if seed is None or int(seed) < 0:
                seed = random.SystemRandom().randint(0, 0xffffffffffffffff)
            else:
                seed = int(seed)

            rng = random.Random(seed)
            selected = rng.choice(prompts)
        else:
            selected = next(p for p in prompts if p["name"] == prompt_name)

        prompt = selected.get("prompt", "")
        negative = selected.get("negative", "")

        # Expose the seed used as a cache-buster output so downstream nodes
        # and the execution engine see a changed output when random mode is used.
        cache_buster = seed if mode == "random" else -1

        print(f"[PromptLibrary] Seed: {seed}")
        print(f"[PromptLibrary] Selected: {selected.get('name', '')}")
        print(f"[PromptLibrary] Prompt: {prompt}")

        return (
            prompt,
            negative,
            cache_buster
        )


class PromptLibraryExtraNode:
    @classmethod
    def INPUT_TYPES(cls):
        prompts = load_prompts()
        names = [p["name"] for p in prompts]

        # TODO: Fix NaN in seed input when left blank despite specifying default.
        # For now it's fine since we depend on RGThree seed anyway
        return {
            "required": {
                "mode": (["random", "select"],),
                "prompt_name": (names,),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
                "timestamp_format": ("STRING", {"default": "%Y%m%d_%H%M%S"}),
                "prefix": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("prompt", "negative", "name", "name_slug", "cache_buster")
    FUNCTION = "run"
    CATEGORY = "Prompt Library"

    def run(self, mode, prompt_name, seed, timestamp_format, prefix, suffix):
        prompts = load_prompts()
        
        if mode == "random":
            if seed is None or int(seed) < 0:
                seed = random.SystemRandom().randint(0, 0xffffffffffffffff)
            else:
                seed = int(seed)

            rng = random.Random(seed)
            selected = rng.choice(prompts)
        else:
            selected = next(p for p in prompts if p["name"] == prompt_name)

        name = selected.get("name", "")
        base_prompt = selected.get("prompt", "")
        negative = selected.get("negative", "")

        # Apply prefix/suffix to POSITIVE prompt
        prompt_parts = [
            prefix.strip(),
            base_prompt.strip(),
            suffix.strip()
        ]
        prompt = ", ".join([p for p in prompt_parts if p])

        base_slug = slugify(name)

        try:
            timestamp = datetime.now().strftime(timestamp_format) if timestamp_format else ""
        except Exception:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        name_slug = "_".join([p for p in [timestamp, base_slug] if p])

        print(f"""
            [PromptLibraryExtra]
            Seed     : {seed}
            Name     : {name}
            Slug     : {name_slug}
            Prompt   : {prompt}
            Negative : {negative}
        """)

        cache_buster = seed if mode == "random" else -1

        # Strange but no matter what I do the output gets cached regardless unless
        # we output some sort of cache buster
        return (
            prompt,
            negative,
            name,
            name_slug,
            cache_buster
        )