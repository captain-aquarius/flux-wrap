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


# ASCII art

txt = "kimi  k2"
font = "small"
logo = text2art("kimi  k2",font="small")

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

# Locate yourself in the file system

PROJECT_DIR = Path(__file__).resolve().parent

# load the TOML

toml = "default.toml"

toml_path = PROJECT_DIR/"templates"/toml

try:
    with toml_path.open("rb") as f:
        toml_data = tomllib.load(f)         # TOML becomes Python dictionary toml_data
except FileNotFoundError:
    sys.exit(f"{toml_path} not found")
except tomllib.TOMLDecodeError as e:
    sys.exit(f"TOML error: {e}")

meta = toml_data.get("meta", {})
if not meta.get("model"):
    sys.exit("TOML must contain [meta].model")

tone_dict = toml_data.get("tones", {})

model = meta["model"]
temp = meta["temperature"]
max_tokens = meta["max_tokens"]
tone = "default"
tone_str = ""
prompt = ""
messages = []
params = [model, messages, temp, max_tokens]

def buildpayload(param_list)->dict:
    model = param_list[0]
    messages = param_list[1]
    temp = param_list[2]
    tokens = int(param_list[3])
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temp,
        "max_tokens": tokens,
    }
    return payload

# The Ritual

while True:

    print(f"\n{logo}\n")
    print(f"Ready to call model '{model}'\nModel/Temperature presets loaded from '{toml}'")
    mode = input("Enter Session Mode (0) or send single prompt (1)? ")

    if mode == "0":
        # tone selection
        tn_list = list(tone_dict.keys())
        tone = input(f"Choose persona: {tn_list} ")
        if tone not in tn_list:
            break
        tone_str = tone_dict[tone].replace("\n", " ").strip()
        messages.append({"role": "system", "content": tone_str})

        while True:
            # prompt declaration
            prompt = input(f"Kimi K2 ({tone}) prompt: ")
            if not prompt:
                break
            messages.append({"role":"user", "content": prompt})
            # max token allocation
            max_tokens = int(input("Max Tokens: "))

            # payload construction

            params = [model, messages, temp, max_tokens]
            payload = buildpayload(params)

            print(f"Here is your payload preview:\n\n{payload}\n\n")
            user = input("Confirm prompt send? Y/n ")
            if user.upper() != "Y":
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
            print(f"{answer}\n")
            messages.append({"role":"assistant","content": answer})
            user = input("Continue? Y/n " )
            if user.upper() != "Y":
                break


    elif mode == "1":
        messages = []
        prompt = input("Kimi K2 prompt: ")
        messages.append({"role":"user","content":prompt})
        max_tokens = int(input("Max Tokens: "))

        params = [model, messages, temp, max_tokens]
        payload = buildpayload(params)
        
        print(f"Here is your payload preview:\n\n{payload}\n\n")
        user = input("Confirm prompt send? Y/n ")
        if user.upper() != "Y":
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
        print(f"{answer}\n")

    else:
        break

    # Save to File
    user = input("Save response to file? Y/n ")
    if mode == "0":
        print("Save to file currently unavailable for Session Mode.")
    elif user.upper() == "Y":
        sep = "-"*len(timestamp)
        entry = (
            f"\n## {timestamp}\n"
            f"\n**Prompt ({tone}):**\n{prompt}\n\n"
            f"**Response:**\n{answer}\n"
            f"\n{sep}\n"
        )
        log_nm = "kimik2_log.md"
        log = PROJECT_DIR/log_nm
        if log.exists():
            with log.open("r", encoding="utf-8") as f:
                old = f.read()
        else:
            old = ""
        with log.open("w", encoding="utf-8") as f:
            f.write(entry + old)
        print(f"Prompt + Response written to file '{log_nm}'")

    again = input("Call Kimi K2 with another prompt? Y/n ")
    if again.upper() != "Y":
        break


# Payload Preview
# print("--- DRY-RUN payload preview ---")
# print(json.dumps({
#      "model": meta["model"],
#     "messages": messages,
#      "temperature": meta.get("temperature", 0.7),
#      "max_tokens": meta.get("max_tokens",256),
#}, indent=2, ensure_ascii=False))
