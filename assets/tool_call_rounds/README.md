# Multi-Round Tool Calling Fixtures

Use these files to manually test whether the assistant can keep calling
`read_text_file` after a tool result reveals a new file path.

Try this prompt:

```text
Follow the file trail starting at assets/tool_call_rounds/start.md. What is the final launch phrase, and what path did you follow?
```

Expected path:

```text
assets/tool_call_rounds/start.md
assets/tool_call_rounds/operations.md
assets/tool_call_rounds/vault.json
assets/tool_call_rounds/final.md
```

Expected final launch phrase:

```text
bright lantern protocol
```

This prompt should require multiple tool-call rounds because each file reveals
only the next file to read.
