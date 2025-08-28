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
from openai import OpenAI

print(f"This is a test of the Kimi K2 API")

load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    sys.exit("No API_KEY located.")

print(f"API_KEY of length {len(api_key)} characters obtained.")

base_url = "https://openrouter.ai/api/v1"



    

