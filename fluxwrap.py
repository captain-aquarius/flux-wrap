#!/usr/bin/env python3
"""
fluxwrap.py - lightweight OpenRouter CLI protocol
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import tomllib
from openai import OpenAI
from art import text2art


print("Attempting to get API KEY >>>")

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

# Retrieve meta + models + tones
meta = toml_data["meta"]
model_dict = toml_data["models"]
tone_dict = toml_data["tones"]

# Initialize required parameters for buildpayload(params:list)->dict:
temp = meta["temperature"]
max_tokens = meta["max_tokens"]
tone = "default"

def buildpayload(param_list:list)->dict:
    """PAYLOAD ASSEMBLY"""
    model, messages, temp, tokens = param_list

    clean_messages = []
    for msg in messages:
        clean_msg = {
                "role": msg["role"],
                "content": " ".join(msg["content"].split())
        }
        clean_messages.append(clean_msg)

    payload = {
        "model": model,
        "messages": clean_messages,
        "temperature": temp,
        "max_tokens": int(tokens),
    }
    return payload

def apidrop(payload:dict)->str:
    """API CALL"""
    try:
        response = client.chat.completions.create(**payload)
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        return f"API error: {e}"

# --- MODEL SELECTION --- #
print("\nThe following models are available via OpenRouter:\n")
model_choices = {}
for i, (m_name,m_descript) in enumerate(model_dict.items(), 1):
    model_choices[i] = m_name
    print(f" {i}: {m_descript}\n")
m_select = input("\nSelection:\n~ ")
if m_select.upper() == "X":
    sys.exit()
model = model_choices[int(m_select)]


#---#ASCII ART GEN#---#

# hide company
txt1 = model.rsplit("/",1)[-1]
# hide 'free' indicator
name = txt1.split(":",1)[0]

logo = text2art(name,font="ogre")

# --- CORE LOOP --- #
while True:

    print(f"\n{logo}\n")
    print(f"Ready to call model '{model.upper()}'\nModel/Temperature/Tone presets loaded from '{toml}'")
    mode = input("Enter Session Mode (0) or send single prompt (1)?\n~ ")
    messages = []
    # --- SESSION LOOP --- #
    if mode == "0":

        # --- TONE SELECTION --- #
        print("\nThe following tones are available:\n")
        tone_choices = {}
        for i, (tn_name,tn_str) in enumerate(tone_dict.items(), 0):
            tone_choices[i] = tn_name
            print(f" {i}: {tn_name.upper()}\n")
        tn_select = input("Selection:\n~ ")
        if tone.upper() == "X":
            sys.exit()
        tone = tone_choices[int(tn_select)]
        if tone != "default":
            messages.append({"role": "system", "content": tone_dict[tone]})            # Add system prompt to messages list

        # --- SESSION LOOP --- #
        while True:

            # prompt declaration
            prompt = input(f"{name.upper()} ({tone}) prompt:\n~ ")
            if not prompt:
                break

            messages.append({"role":"user", "content": prompt})             # Add user prompt to messages list

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
            print(f"--- {name.upper()} says ---\n")
            print(f"{answer}\n")

            messages.append({"role":"assistant","content": answer})         # Add response to messages list

            # Consent to re-loop/continue SESSION LOOP
            user = input("Continue? Y/n\n~ " )

            if user.upper() not in ("Y",""):
                break

    #---SINGLE-PROMPT LOOP---#
    elif mode == "1":
        tone = "default"
        messages = []
        prompt = input(f"{name.upper()} ({tone}) prompt:\n~ ")
        messages.append({"role":"user","content":prompt})                   # Add user prompt to messages list
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
        print(f"--- {name.upper()} says ---\n")
        print(f"{answer}\n")

        messages.append({"role":"assistant","content": answer})             # Add response to messages list

    else:
        break

    # Save to File
    user = input("Save response to file? Y/n\n~ ")
    if user.upper() not in ("Y",""):
        continue
    else:
        if mode == "0":
            print(f"Session will be saved in today's {tone.upper()} session file.")
        else:
            print(f"Response will be saved to '{name}_log.md'")

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
                        f"\n*{name} Response:*\n{ans}\n"
                        "\n---\n"
                )
                entries.append(entry)
        session = ''.join(entries)

        if mode == "0":
            date = datetime.now().strftime("%m_%d_%Y")
            log_file = f"{date}_{tone}.md"
            tn_folder = PROJECT_DIR/"sessions"/tone.upper()
            tn_folder.mkdir(exist_ok=True)
            log = tn_folder/log_file


        elif mode == "1":
            log_file = f"{name}_log.md"
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
        print(f"Saved in '{log_file}'")
    
    # Consent to re-loop/continue CORE LOOP
    again = input(f"Call {model.upper()} with another prompt? Y/n\n~ ")
    if again.upper() not in ("Y",""):
        break
