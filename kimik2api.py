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


print(f"You are attempting to interface with Kimi K2 through the OpenRouter system.\nAttempting to get API KEY >>>")

# Get API Key from .env
load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    sys.exit("No API_KEY located.")
print(f"API_KEY of length {len(api_key)} characters obtained.")

# Initialize OpenRouter
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
        toml_data = tomllib.load(f)                                         # TOML becomes Python dictionary toml_data
except FileNotFoundError:
    sys.exit(f"{toml_path} not found")
except tomllib.TOMLDecodeError as e:
    sys.exit(f"TOML error: {e}")

# Retrieve metadata + tones
meta = toml_data.get("meta", {})
if not meta.get("model"):
    sys.exit("TOML must contain [meta].model")
tone_dict = toml_data.get("tones", {})

# Initialize required parameters for buildpayload(params:list)->dict:
model = meta["model"]
temp = meta["temperature"]
max_tokens = meta["max_tokens"]
tone = "default"

def buildpayload(param_list:list)->dict:
    """PAYLOAD ASSEMBLY"""
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

def apidrop(payload:dict)->str:
    """API CALL"""
    try:
        response = client.chat.completions.create(**payload)
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        sys.exit(f"API error: {e}")


# ASCII art
txt1 = model.rsplit("/",1)[-1]
txt2 = txt1.split(":",1)[0]
logo = text2art(txt2,font="small")

# CORE LOOP
while True:

    print(f"\n{logo}\n")
    print(f"Ready to call model '{model}'\nModel/Temperature/Tone presets loaded from '{toml}'")
    mode = input("Enter Session Mode (0) or send single prompt (1)?\n~ ")
    messages = []

    if mode == "0":

        # tone selection
        tn_list = list(tone_dict.keys())
        menu = "\n".join(tn_list)
        tone = input(f"\nChoose Persona:\n---\n{menu}\n---\n~ ")
        if tone not in tn_list:
            break
        tone_str = tone_dict[tone].replace("\n", " ").strip()
        messages.append({"role": "system", "content": tone_str})            # Add system prompt to messages list

        # SESSION LOOP
        while True:

            # prompt declaration
            prompt = input(f"{model} ({tone}) prompt:\n~ ")
            if not prompt:
                break

            messages.append({"role":"user", "content": prompt.strip()})             # Add user prompt to messages list

            # max token allocation
            budget = input("Max Tokens:\n~ ")
            max_tokens = int(budget) if budget else max_tokens

            # payload construction
            params = [model, messages, temp, max_tokens]                    # Build parameter list for buildpayload()
            payload = buildpayload(params)

            # Payload Preview                                               # (nonessential) Display of payload and final consent
            print(f"Here is your payload preview:\n\n{payload}\n\n")
            user = input("Confirm prompt send? Y/n\n~ ")
            if user.upper() not in ("Y",""):
                break

            print("\n>>> calling OpenRouter ...\n")
            
            # API CALL
            answer = apidrop(payload)
            
            timestamp = datetime.now().strftime("%m-%d-%Y @ %I:%M%p")       # get the date+time of response as a string

            # Print to CLI
            print(timestamp)
            print(f"--- {model} says ---\n")
            print(f"{answer}\n")

            messages.append({"role":"assistant","content": answer.strip()})         # Add response to messages list

            # Consent to re-loop/continue SESSION LOOP
            user = input("Continue? Y/n\n~ " )

            if user.upper() not in ("Y",""):
                break

    # SINGLE-PROMPT LOOP

    elif mode == "1":
        tone = "default"
        messages = []
        prompt = input(f"{model} ({tone}) prompt:\n~ ")
        messages.append({"role":"user","content":prompt.strip()})                   # Add user prompt to messages list
        budget = input("Max Tokens:\n~ ")
        max_tokens = int(budget) if budget else max_tokens

        params = [model, messages, temp, max_tokens]
        payload = buildpayload(params)

        print(f"Here is your payload preview:\n\n{payload}\n\n")
        user = input("Confirm prompt send? Y/n\n~ ")
        if user.upper() not in ("Y",""):
            break

        print("\n>>> calling OpenRouter ...\n")

        # The API CALL
        answer = apidrop(payload)

        timestamp = datetime.now().strftime("%m-%d-%Y @ %I:%M%p")

        print(timestamp)
        print(f"--- {model} says ---\n")
        print(f"{answer}\n")

        messages.append({"role":"assistant","content": answer.strip()})             # Add response to messages list

    else:
        break

    # Save to File
    user = input("Save response to file? Y/n\n~ ")
    if user.upper() not in ("Y",""):
        continue
    else:
        if mode == "0":
            print(f"Session will be saved in today's {tone} session file.")
        else:
            print("Session will be saved to master log.")

        # extract content of messages list in desired markdown format
        entries = []
        for dic in messages:
            if dic["role"] == "system":
                pass
            elif dic["role"] == "user":
                prm = dic["content"]
                entry = (
                    f"\n*Prompt ({tone}):*\n{prm}\n\n"
                )
                entries.append(entry)
            elif dic["role"] == "assistant":
                ans = dic["content"]
                entry = (
                        f"\n*Response:*\n{ans}\n"
                        "\n---\n"
                )
                entries.append(entry)
        session = ''.join(entries)

        if mode == "0":
            date = datetime.now().strftime("%m_%d_%Y")
            log_file = f"{date}_{tone}.md"
            log = PROJECT_DIR/"sessions"/log_file
        elif mode == "1":
            log_file = "kimik2_log.md"
            log = PROJECT_DIR/log_file
        else:
            break

        if log.exists():
            with log.open("r", encoding="utf-8") as f:
                old = f.read()
        else:
            old = ""

        with log.open("w", encoding="utf-8") as f:
            f.write(f"\n## {timestamp}\n" + session + old)
        print(f"Session written to file '{log_file}'")
    
    # Consent to re-loop/continue CORE LOOP
    again = input("Call Kimi K2 with another prompt? Y/n\n~ ")
    if again.upper() not in ("Y",""):
        break
