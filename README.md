# AI CLI Assistant

A small command-line AI assistant for learning how to build agentic AI with the OpenAI API.

This project follows the roadmap in `FUNCTIONAL_SPEC.md`. The current version is:

## v0.6 - Streaming Responses

The app currently:

- Loads an OpenAI API key from a local `.env` file.
- Starts a simple terminal chat loop.
- Shows a help menu for supported commands.
- Stores conversation history so the assistant can answer follow-up questions.
- Saves conversation history to `conversation_history.json`.
- Reloads saved conversation history when the app starts.
- Lets the user clear saved conversation history.
- Detects supported text file paths in user messages.
- Reads local `.txt`, `.md`, `.py`, `.json`, and `.csv` files.
- Supports multiple file paths in a single user message.
- Keeps file contents in runtime file memory so repeated references do not need to reread the file from disk.
- Adds each referenced file's contents to the model input once so the assistant can summarize or answer questions about the files.
- Requests structured assistant responses using a JSON Schema.
- Parses each model response into fields for `answer`, `summary`, `files_used`, and `follow_up_questions`.
- Streams model response events internally while collecting structured JSON output.
- Shows a thinking indicator while waiting for streamed response events.
- Handles failed, incomplete, and error stream events gracefully.
- Prints the assistant's answer, files used, and follow-up questions.
- Prints token usage after each successful model response.
- Saves usage log entries to `usage_log.jsonl`.
- Logs successful model responses, JSON parse errors, and model response errors.
- Includes token usage, user input, success status, and files used when available in usage logs.
- Lets the user show total token usage.
- Lets the user show the detailed usage log.
- Exits when the user types `exit`, `quit`, or `bye`.
- Exits cleanly when the user presses Ctrl+C.

`conversation_history.json` and `usage_log.jsonl` are ignored by git because they may contain local chat data.

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

Ask about multiple supported files:

```text
𖨆 : compare README.md and FUNCTIONAL_SPEC.md
```

Ask a follow-up question that relies on earlier context:

```text
𖨆 : what version did you say this project is on?
```

Show the saved conversation history:

```text
history
```

Show files cached during the current run:

```text
file history
```

Show total token usage:

```text
usage
```

Show the detailed usage log:

```text
log
```

Show available commands:

```text
help
```

Clear the saved conversation history and runtime file memory:

```text
clear
```

To stop the app, type:

```text
exit
```

## Test

The current unit tests were generated with AI assistance as a learning scaffold.
Review and adjust them as the app behavior changes.

Run the test suite:

```bash
python3 -m unittest discover -s tests
```

## Possible Future Features

- Read more text-based file types.
- Ask questions across multiple files more deeply.
- Summarize an entire folder.
- Stream the final answer text directly in the terminal.
- Add real OpenAI tool calling for filesystem actions.
- Let the user choose the model from `.env`.
- Add commands for deleting or exporting conversation history.
- Add safer limits for very large files.
- Improve usage log formatting for easier reading.
- Save file history between app runs.

## Project Roadmap

- v0.1 - Basic chatbot using the Responses API.
- v0.2 - File reader tool.
- v0.3 - Conversation history.
- v0.4 - Structured outputs.
- v0.5 - Logging and token usage.
- v0.6 - Streaming responses.
