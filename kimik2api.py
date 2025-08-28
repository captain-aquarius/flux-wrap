#!/usr/bin/env python3
"""
kimik2api.py - minimal Kimi K2 CLI starter
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import tomllib
import json
from openai import OpenAI

print(f"This is a test of the Kimi K2 API")

load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    sys.exit("No API_KEY located.")

print(f"API_KEY of length {len(api_key)} characters obtained.")

base_url = "https://openrouter.ai/api/v1"
client = OpenAI(
        base_url=base_url,
        api_key=api_key
)

req_path = Path("requests/hello.toml")
try:
    with req_path.open("rb") as f:
        toml_data = tomllib.load(f)
except FileNotFoundError:
    sys.exit(f"{req_path} not found")
except tomllib.TOMLDecodeError as e:
    sys.exit(f"TOML error: {e}")

meta = toml_data.get("meta", {})
messages = toml_data.get("messages", [])
if not meta.get("model") or not isinstance(messages, list) or not messages:
    sys.exit("TOML must contain [meta].model and at least one [[messages]]")

print(f"Ready to call model '{meta['model']}' with {len(messages)} message(s)")

# Payload Preview
# print("--- DRY-RUN payload preview ---")
# print(json.dumps({
#      "model": meta["model"],
#     "messages": messages,
#      "temperature": meta.get("temperature", 0.7),
#      "max_tokens": meta.get("max_tokens",256),
#}, indent=2, ensure_ascii=False))

kwargs = {
    "model": meta["model"],
    "messages": messages,
    "temperature": meta.get("temperature", 0.7),
    "max_tokens": meta.get("max_tokens",256),
}

print("\n>>> calling OpenRouter ...")
try:
    response = client.chat.completions.create(**kwargs)
    answer = response.choices[0].message.content.strip()
except Exception as e:
    sys.exit(f"API error: {e}")

print("\n---Kimi K2 says ---")
print(answer)


