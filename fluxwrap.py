#!/usr/bin/env python3
"""
FluxWrap - OpenRouter CLI protocol
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import tomllib
from openai import OpenAI
from art import text2art
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# call UI Console
console = Console()

#print FluxWrap logo
logo = text2art("FluxWrap","ogre")
console.print(Panel(logo,width=57,style="bold bright_yellow"))

# Get API Key from .env
load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    sys.exit("No API_KEY located.")

# Initialize OpenRouter
base_url = "https://openrouter.ai/api/v1"
client = OpenAI(
        base_url=base_url,
        api_key=api_key
)

# Locate yourself in the file system
PROJECT_DIR = Path(__file__).resolve().parent

# Retreive directory for saving sessions and a private TOML config
save_dir_str = os.getenv("SAVE_DIR")
private_config_str = os.getenv("PRIVATE_CONFIG")

if save_dir_str:
    SAVE_DIR = Path(os.path.expanduser(save_dir_str))
    console.print(Panel(f"Save Directory = {save_dir_str}", width=57))
else:
    SAVE_DIR = PROJECT_DIR

if private_config_str:
    PRIVATE_CONFIG = Path(os.path.expanduser(private_config_str))
    console.print(Panel(f"Private Config = {private_config_str}", width=57))
else:
    PRIVATE_CONFIG = None
    console.print("No path to private config file found.", style="bold red")

# load the TOML config
toml = "flux_config.toml"
toml_path = PROJECT_DIR/toml
try:
    with toml_path.open("rb") as f:
        toml_data = tomllib.load(f)                                         
        console.print(Panel(f"Default Config = {toml_path}"), width=57)
except FileNotFoundError:
    sys.exit(f"{toml} not found")
except tomllib.TOMLDecodeError as e:
    sys.exit(f"TOML error: {e}")

# Load and merge private config if it exists
if PRIVATE_CONFIG and PRIVATE_CONFIG.exists():
    try:
        with PRIVATE_CONFIG.open("rb") as f:
            private_data = tomllib.load(f)
            # Merge private tones into base config
            toml_data["tones"].update(private_data.get("tones", {}))
            toml_data["models"].update(private_data.get("models",{}))
            console.print(
                Panel(
                    "Default and Private Configs Merged", 
                    width=57
                ), 
                style="bold magenta"
            )
    except tomllib.TOMLDecodeError as e:
        console.print(f"Private TOML error: {e}", style="bold red")
        # Continue with base config only
    except FileNotFoundError:
        console.print(
            f"Private config file not found at {PRIVATE_CONFIG}", 
            style="bold red"
        )
else:
    console.print(f"Private config file not found.", style="bold red")

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

def beautify(answer:str, model_name:str):
    md = Markdown(answer, code_theme="dracula")
    panel = Panel(
            md,
            title=f"[bold bright_yellow]{model_name}[/]",
            border_style="bright_magenta",
            subtitle=f"[italic bright_magenta]{timestamp}[/]",
            padding=(1,2)
    )
    console.print(panel)

# --- MAIN PROGRAM LOOP --- #
while True:

    # --- MODEL SELECTION --- #
    print("\nThe following models are available via OpenRouter:\n")
    model_choices = {}
    for i, (m_name,m_descript) in enumerate(model_dict.items(), 1):
        model_choices[i] = m_name
        console.print(
            f"[bright_yellow] {i}:[/] [bold bright_blue]{m_descript}[/]\n"
        )
    m_select = input("\nModel Selection (X to Exit):\n~ ")
    if m_select.upper() == "X":
        break
    model = model_choices[int(m_select)]


    # --- ASCII ART GEN --- #

    txt1 = model.rsplit("/",1)[-1]
    name = txt1.split(":",1)[0]
    mod_logo = text2art(name,font="tarty3")

    # --- CORE LOOP --- #
    while True:

        console.print(Panel(f"\n{mod_logo}\n",style="bold bright_magenta"))
        print(
            f"Ready to call model '{model.upper()}'"
            f"\nModel/Temperature/Tone presets loaded from '{toml}'"
        )
        mode = input("Enter Session Mode (0) or send single prompt (1)?\n~ ")
        messages = []

        # --- SESSION LOOP --- #
        if mode == "0":

            # --- TONE SELECTION --- #
            print("\nThe following tones are available:\n")
            tone_choices = {}
            for i, (tn_name,tn_str) in enumerate(tone_dict.items(), 0):
                tone_choices[i] = tn_name
                console.print(
                    f"[bright_yellow] {i}:[/] [bold bright_magenta]{tn_name.upper()}[/]\n"
                )
            tn_select = input("Tone Selection:\n~ ")
            if tn_select.upper() == "X":
                break
            tone = tone_choices[int(tn_select)]
            if tone != "default":
                messages.append(
                    {
                        "role": "system", 
                        "content": tone_dict[tone]
                    }
                )            

            # --- SESSION LOOP --- #
            while True:

                # prompt declaration
                prompt = input(f"{name.upper()} ({tone}) prompt:\n~ ")
                if prompt.upper() in ("X",""):
                    break

                messages.append(
                    {
                        "role":"user", 
                        "content": prompt
                    }
                )             

                # max token allocation
                budget = input(f"Max Tokens ({max_tokens}):\n~ ")
                if budget.upper() == "X":
                    break
                max_tokens = int(budget) if budget else max_tokens

                # custom temp setting
                user_temp = input(f"Temperature ({temp}):\n~ ")
                if user_temp.upper() == "X":
                    break
                temp = float(user_temp) if user_temp else temp

                # payload construction
                params = [model, messages, temp, max_tokens]                    
                payload = buildpayload(params)

                # Payload Preview                                               
                print(f"Here is your payload preview:\n\n")
                console.print(Panel(f"{payload}"))
                user = input("\nConfirm prompt send? Y/n\n~ ")
                if user.upper() not in ("Y",""):
                    break

                # API CALL
                
                with console.status(
                        "[bold yellow]Calling OpenRouter...[/]", 
                        spinner="aesthetic"
                ) as status:
                    answer = apidrop(payload)

                timestamp = datetime.now().strftime("%m-%d-%Y @ %I:%M%p")       

                messages.append(
                    {
                        "role":"assistant",
                        "content": answer
                    }
                )         

                beautify(answer, name)

                # Consent to re-loop/continue SESSION LOOP
                user = input("Continue? Y/n\n~ " )

                if user.upper() not in ("Y",""):
                    break

        #---SINGLE-PROMPT LOOP---#
        elif mode == "1":
            tone = "default"
            messages = []
            prompt = input(f"{name.upper()} ({tone}) prompt:\n~ ")
            messages.append(
                {
                    "role":"user",
                    "content":prompt
                }
            )                   
            budget = input(f"Max Tokens ({max_tokens}):\n~ ")
            max_tokens = int(budget) if budget else max_tokens
            user_temp = input(f"Temperature ({temp}):\n~")
            temp = float(user_temp) if user_temp else temp
            params = [model, messages, temp, max_tokens]
            payload = buildpayload(params)

            print(f"Here is your payload preview:\n\n{payload}\n\n")
            user = input("Confirm prompt send? Y/n\n~ ")
            if user.upper() not in ("Y",""):
                break

            print("\n>>> calling OpenRouter >>>\n")

            # The API CALL
            answer = apidrop(payload)
            timestamp = datetime.now().strftime("%m-%d-%Y @ %I:%M%p")

            print(timestamp)
            print(f"--- {name.upper()} says ---\n")
            print(f"{answer}\n")

            messages.append(
                {
                    "role":"assistant",
                    "content": answer
                }
            )             

        else:
            break

        # Save to File
        if prompt.upper() in ("X",""):
            break
        user = input("Save response to file? Y/n\n~ ")
        if user.upper() not in ("Y",""):
            continue
        else:
            if mode == "0":
                print(
                    f"Session will be saved in today's {tone.upper()} session file."
                )
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
                tn_folder = SAVE_DIR/tone.upper()
                tn_folder.mkdir(exist_ok=True)
                log = tn_folder/log_file

            elif mode == "1":
                log_file = f"{name}_log.md"
                log = SAVE_DIR/log_file

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
