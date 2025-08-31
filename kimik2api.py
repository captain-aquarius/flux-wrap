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
from art import text2art


print(f"You are attempting to interface with Kimi K2 through the OpenRouter system.")

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

PROJECT_DIR = Path(__file__).resolve().parent
template="default.toml"

req_path = PROJECT_DIR/"templates"/template
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

txt = "kimi  k2"
font = "small"
logo = text2art("kimi  k2",font="small")

# Payload Preview
# print("--- DRY-RUN payload preview ---")
# print(json.dumps({
#      "model": meta["model"],
#     "messages": messages,
#      "temperature": meta.get("temperature", 0.7),
#      "max_tokens": meta.get("max_tokens",256),
#}, indent=2, ensure_ascii=False))

while True:

    print(f"\n{logo}\n")
    print(f"Ready to call model '{meta['model']}' with {len(messages)} message(s)")

    mode = input("Send (0) TOML template or (1) custom prompt? ")
    if mode == "0":
        payload = {
            "model": meta["model"],
            "messages": messages,
            "temperature": meta.get("temperature", 0.7),
            "max_tokens": meta.get("max_tokens",256),
        }
    elif mode == "1":
        print(f"Model/Temperature Presets Loaded from {req_path} ")
        message = input("Kimi K2 prompt: ")
        max_tokens = int(input("Max Tokens: "))
        payload = {
            "model": meta["model"],
            "messages": [{"role": "user", "content": message}],
            "temperature": meta.get("temperature", 0.7),
            "max_tokens": max_tokens,
        }
    else:
        break

    print("\n>>> calling OpenRouter ...\n")
    try:
        response = client.chat.completions.create(**payload)
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        sys.exit(f"API error: {e}")

    now = datetime.now()
    timestamp = now.strftime("%m-%d-%Y @ %I:%M%p")
    print(timestamp)
    print("--- Kimi K2 says ---\n")
    print(answer)

    user = input("Save response to file? Y/n ")
    if user.upper() == "Y":
        sep = "-"*len(timestamp)
        entry = (
            f"\n## {timestamp}\n"
            f"\n**Prompt:**\n{message}\n\n"
            f"**Response:**\n{answer}\n"
            f"\n{sep}\n"
        )
        log = PROJECT_DIR/"kimik2_log.md"
        if log.exists():
            with log.open("r", encoding="utf-8") as f:
                old = f.read()
        else:
            old = ""
        with log.open("w", encoding="utf-8") as f:
            f.write(entry + old)
        print(f"Prompt + Response written to file {log}")

    again = input("Call Kimi K2 with another prompt? Y/n ")
    if again.upper() != "Y":
        break


