# AI CLI Assistant

A small command-line AI assistant for learning how to build agentic AI with the OpenAI API.

This project follows the roadmap in `FUNCTIONAL_SPEC.md`. The current version is:

## v0.1 - Basic Chatbot

The app currently:

- Loads an OpenAI API key from a local `.env` file.
- Starts a simple terminal chat loop.
- Sends each user message to the OpenAI Responses API.
- Prints the assistant's response.
- Exits when the user types `exit`, `quit`, or `bye`.

Later versions will add file reading, conversation history, structured outputs, logging, token usage, and streaming.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

The `.env` file is ignored by git so the API key is not committed.

## Run

```bash
python3 main.py
```

Then type a message at the prompt:

```text
𖨆 : hello
```

To stop the app, type:

```text
exit
```

## Project Roadmap

- v0.1 - Basic chatbot using the Responses API.
- v0.2 - File reader tool.
- v0.3 - Conversation history.
- v0.4 - Structured outputs.
- v0.5 - Logging and token usage.
- v0.6 - Streaming responses.
