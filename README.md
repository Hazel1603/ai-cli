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

Future branches will follow the same pattern:

- `feature/v0.6` - Streaming responses.

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

The goal is to keep each step small and understandable before adding more agent-like behavior.
