# AI CLI Assistant

A small command-line project for learning how to build an agentic AI assistant with the OpenAI API.

This repo is organized as a learning path. The `main` branch is the landing page and roadmap. Each milestone lives on its own branch so you can inspect the project one step at a time.

## Branches

| Branch | Status | What it shows |
| --- | --- | --- |
| `main` | Overview | Project roadmap and branch navigation. |
| `feature/v0.1` | Available | Basic chatbot using the OpenAI Responses API. |
| `feature/v0.2` | Available | File reader tool for reading local text files. |
| `feature/v0.3` | Available | Conversation history with saved JSON history, clear/history commands, and runtime file memory. |
| `feature/v0.4` | Available | Structured outputs with JSON Schema responses, parsed answer fields, files used, and follow-up questions. |
| `feature/v0.5` | Available | Logging and token usage with JSONL usage logs, token totals, and usage/log commands. |
| `feature/v0.6` | Available | Streaming response events, thinking indicator, stream error handling, and clean Ctrl+C exit. |
| `feature/v0.7` | Available | Real OpenAI tool calling with a `read_text_file` function tool and multi-round tool loops. |

## How To Navigate

Start from `main` to read the roadmap:

```bash
git checkout main
```

To view and run the first working version:

```bash
git checkout feature/v0.1
```

To view the file reader version:

```bash
git checkout feature/v0.2
```

To view the conversation history version:

```bash
git checkout feature/v0.3
```

To view the structured outputs version:

```bash
git checkout feature/v0.4
```

To view the logging and token usage version:

```bash
git checkout feature/v0.5
```

To view the streaming responses version:

```bash
git checkout feature/v0.6
```

To view the real tool-calling version:

```bash
git checkout feature/v0.7
```

After switching branches, read that branch's `README.md` for setup and run instructions.

To see all local branches:

```bash
git branch
```

To return to the overview:

```bash
git checkout main
```

## Learning Roadmap

The project follows the plan in `FUNCTIONAL_SPEC.md`:

- v0.1 - Basic chatbot using the Responses API.
- v0.2 - File reader tool.
- v0.3 - Conversation history, JSON persistence, history commands, multiple file references, and runtime file memory.
- v0.4 - Structured outputs with JSON Schema responses.
- v0.5 - Logging and token usage.
- v0.6 - Streaming responses.
- v0.7 - Real OpenAI tool calling for filesystem actions.

The goal is to keep each step small and understandable before adding more agent-like behavior.

## Possible Project 1 Extensions

After v0.7, good optional features include:

- Folder summarization.
- Deeper multi-file question answering.
- Visible streaming of the final answer text.
- Safer handling for very large files.
- Exporting or deleting conversation history.

## Next Projects

This repo covers Project 1: AI CLI Assistant. Natural follow-up projects are:

- Project 2 - Personal Knowledge Assistant: embeddings, vector DBs, and retrieval.
- Project 3 - Coding Assistant: code search, bug finding, tests, and refactoring.
- Project 4 - Research Agent: web search, source ranking, summaries, and citations.
- Project 5 - Travel Planner: weather, attractions, maps, budgets, and multiple tools.
- Project 6 - Expense Agent: OCR, categorization, budgeting, and CSV export.
- Project 7 - Meeting Assistant: calendar, email, agendas, and meeting notes.
- Project 8 - Software Engineer Agent: failing tests, logs, documentation search, patches, and PR descriptions.
