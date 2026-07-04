# AI CLI Assistant

A small command-line AI assistant for learning how to build agentic AI with the OpenAI API.

This project follows the roadmap in `FUNCTIONAL_SPEC.md`. The current version is:

## v0.2 - File Reader Tool

The app currently:

- Loads an OpenAI API key from a local `.env` file.
- Starts a simple terminal chat loop.
- Sends each user message to the OpenAI Responses API.
- Detects supported text file paths in user messages.
- Reads local `.txt`, `.md`, `.py`, `.json`, and `.csv` files.
- Adds file contents to the model input so the assistant can summarize or answer questions about the file.
- Prints the assistant's response.
- Exits when the user types `exit`, `quit`, or `bye`.

Later versions will add conversation history, structured outputs, logging, token usage, and streaming.

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

Ask about a supported local text file:

```text
𖨆 : summarize README.md
```

You can also ask questions about a file:

```text
𖨆 : what does testdoc.md say about setup?
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
