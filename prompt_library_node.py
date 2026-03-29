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
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "negative")
    FUNCTION = "run"
    CATEGORY = "Prompt Library"

    def run(self, mode, prompt_name):
        prompts = load_prompts()

        if mode == "random":
            selected = random.choice(prompts)
        else:
            selected = next(p for p in prompts if p["name"] == prompt_name)

        return (
            selected.get("prompt", ""),
            selected.get("negative", "")
        )


# Personally using this for my workflows so I have a consistent naming convention for outputs.
import random
from datetime import datetime
import re


def slugify(name: str):
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)
    return name.strip('_')


class PromptLibraryExtraNode:
    @classmethod
    def INPUT_TYPES(cls):
        prompts = load_prompts()
        names = [p["name"] for p in prompts]

        return {
            "required": {
                "mode": (["random", "select"],),
                "prompt_name": (names,),
                "timestamp_format": ("STRING", {"default": "%Y%m%d_%H%M%S"}),
                "prefix": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "negative", "name", "name_slug")
    FUNCTION = "run"
    CATEGORY = "Prompt Library"

    def run(self, mode, prompt_name, timestamp_format, prefix, suffix):
        prompts = load_prompts()

        # Select prompt
        if mode == "random":
            selected = random.choice(prompts)
        else:
            selected = next(p for p in prompts if p["name"] == prompt_name)

        name = selected.get("name", "")
        base_prompt = selected.get("prompt", "")
        negative = selected.get("negative", "")

        # ✅ Apply prefix/suffix to POSITIVE PROMPT
        prompt_parts = [
            prefix.strip(),
            base_prompt.strip(),
            suffix.strip()
        ]
        prompt = ", ".join([p for p in prompt_parts if p])

        # ✅ Slug is independent (clean, reproducible)
        base_slug = slugify(name)

        timestamp = ""
        if timestamp_format:
            try:
                timestamp = datetime.now().strftime(timestamp_format)
            except Exception:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        slug_parts = [
            base_slug,
            timestamp
        ]

        name_slug = "_".join([p for p in slug_parts if p])

        return (
            prompt,
            negative,
            name,
            name_slug
        )