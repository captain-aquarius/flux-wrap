# GEMINI.md

This file provides a comprehensive overview of the `flux-wrap` project, its purpose, and how to interact with it.

## Project Overview

**FluxWrap** is a Python-based command-line interface (CLI) for interacting with the OpenRouter API. It simplifies the process of sending prompts to various large language models (LLMs) and managing conversational context.

The key features of FluxWrap include:

*   **Model Selection**: Users can choose from a predefined list of LLMs available through the OpenRouter API.
*   **Tone Customization**: Users can apply "tones" to their conversations, which are system prompts that influence the LLM's response style. These tones are configurable via a `default.toml` file.
*   **Session Management**: The script supports both single-prompt interactions and multi-turn conversational sessions, where the context is maintained.
*   **Conversation Logging**: Conversations can be saved as Markdown files for later review.

The project is built using Python and relies on the `openai` library to interact with the OpenRouter API. It also uses `tomllib` to parse the configuration file and `python-dotenv` to manage API keys.

## Building and Running

To run this project, you will need Python 3 and the dependencies listed in `requirements.txt`.

**1. Set up the Environment:**

It is recommended to use a virtual environment to manage the project's dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**2. Install Dependencies:**

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

**3. Configure API Key:**

The script requires an OpenRouter API key to function. Create a `.env` file in the project's root directory and add your API key to it:

```
API_KEY="YOUR_OPENROUTER_API_KEY"
```

**4. Run the Script:**

Once the dependencies are installed and the API key is configured, you can run the script:

```bash
python3 fluxwrap.py
```

## Development Conventions

*   **Configuration**: The project uses a TOML file (`templates/default.toml`) for configuring models, tones, and other settings. This allows for easy customization without modifying the source code.
*   **System Prompts**: The "tones" are implemented as system prompts that are sent to the LLM at the beginning of a session. This is a common and effective way to guide the model's behavior.
*   **API Interaction**: The script uses the `openai` Python library to interact with the OpenRouter API. This is a standard practice for interacting with OpenAI-compatible APIs.
*   **File Structure**: The project is organized with the main script (`fluxwrap.py`) in the root directory and templates in a separate `templates` directory. This separation of concerns makes the project easy to navigate.
*   **Saving Sessions**: The script saves session logs in a directory specified in the `default.toml` file. This is a useful feature for keeping a record of interactions with the LLMs.
