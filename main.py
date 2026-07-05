from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import sys
import re
import json
import time

# global variable to store conversation history
MODEL_NAME = None
MAX_TOOL_CALL_ROUNDS = 5
HISTORY_FILE = Path("conversation_history.json")
LOG_FILE = Path("usage_log.jsonl")
TEXT_FILE_TYPES = {".txt", ".md", ".py", ".json", ".csv"}

ASSISTANT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
            "description": "The assistant response to show to the user."
        },
        "summary": {
            "type": "string",
            "description": "A brief summary of the assistant's response."
        },
        "files_used": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "File paths used to answer the question."
        },
        "follow_up_questions": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Helpful follow-up questions the user might ask."
        }
    },
    "required": [
        "answer",
        "summary",
        "files_used",
        "follow_up_questions"
    ],
    "additionalProperties": False
}

# Tool definition for reading text files
READ_TEXT_FILE_TOOL = {
    "type": "function",
    "name": "read_text_file",
    "description": (
        "Read a local text file when the user asks about a file. "
        "Supports .txt, .md, .py, .json, and .csv files."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The local file path to read."
            }
        },
        "required": ["path"],
        "additionalProperties": False
    },
    "strict": True
}


# User input handling functions
def should_exit(user_input):
    return user_input.lower() in {"exit", "quit", "bye"}

def should_clear(user_input):
    return user_input.lower() in {"clear", "reset", "forget"}

def should_show_history(user_input):
    return user_input.lower() in {"history", "show history", "conversation history"}

def should_show_file_history(user_input):
    return user_input.lower() in {"file history", "show file history"}

def should_show_usage(user_input):
    return user_input.lower() in {"usage", "show usage", "token usage"}

def should_show_log(user_input):
    return user_input.lower() in {"log", "show log", "usage log"}

def should_show_help(user_input):
    return user_input.lower() in {"help", "show help", "commands"}

def print_help():
    help_text = """
모 : Here are some commands you can use:
- 'exit', 'quit', 'bye' : Exit the application.
- 'clear', 'reset', 'forget' : Clear the conversation history.
- 'history', 'show history', 'conversation history' : Show the conversation history.
- 'file history', 'show file history' : Show the file history.
- 'usage', 'show usage', 'token usage' : Show the total token usage.
- 'log', 'show log', 'usage log' : Show the detailed usage log.
You can also ask questions or provide input as usual. If you include a file path (e.g., './example.txt'), the assistant will read the file and use its content to answer your question.
"""
    print(help_text)


# Validation Methods
def validate_openai_api_key():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("모 : ∘ ∘ ∘ ( °ヮ° ) ? OPENAI_API_KEY is not set. Add it to your .env file and try again! (˶ᵔᗜᵔ˶)ﾉﾞ")
        sys.exit(1)
    else:
        print("모 : (•̀ᴗ•́ )و OPENAI_API_KEY is set. Proceeding...")
        return api_key

def validate_openai_model():
    global MODEL_NAME
    load_dotenv()

    MODEL_NAME = os.getenv("OPENAI_MODEL")

    if not MODEL_NAME:
        print("모 : ∘ ∘ ∘ ( °ヮ° ) ? OPENAI_MODEL is not set. Add it to your .env file and try again! (˶ᵔᗜᵔ˶)ﾉﾞ")
        sys.exit(1)
    else:
        print(f"모 : (•̀ᴗ•́ )و OPENAI_MODEL is set to '{MODEL_NAME}'. Proceeding...")
        return MODEL_NAME

# Default data object creation functions
def create_default_metadata():
    return {
        "timestamp": datetime.now().isoformat(),
        "used_file": False,
        "file_paths": [],
        "response_output": {}
    }

def create_empty_token_usage():
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }

def create_default_logging():
    return {
        "timestamp": datetime.now().isoformat(),
        "event": "",
        "user_input": "",
        "token_usage": create_empty_token_usage(),
        "success": True
    }


# Text file Tool Functions
def find_text_file_paths(user_input):
    matches = re.findall(
        r"(?:\.\/)?(?:[\w.-]+\/)*[\w.-]+\.(?:txt|md|py|json|csv)\b",
        user_input
    )

    return list(dict.fromkeys(matches))

def read_text_file(file_history, user_filename):
    if user_filename in file_history:
        # print("모 : ^⎚-⎚^ Reading file from history...")
        return file_history[user_filename]

    path = Path(user_filename)

    if path.exists() and path.is_file() and path.suffix.lower() in TEXT_FILE_TYPES:
        # print("모 : ^⎚-⎚^ Reading file...")
        file_content = path.read_text(encoding="utf-8")
        save_file_history(file_history, user_filename, file_content)
        return file_content
    else:
        return None

def execute_read_text_file_tool(file_history, arguments):
    # print("모 : ^⎚-⎚^ Executing read file tool...")
    try:
        tool_args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Tool arguments were not valid JSON."
        }), None

    file_path = tool_args.get("path")
    if not file_path:
        return json.dumps({
            "success": False,
            "error": "Missing required argument: path."
        }), None

    file_content = read_text_file(file_history, file_path)

    if file_content is None:
        return json.dumps({
            "success": False,
            "path": file_path,
            "error": "Could not read that supported text file."
        }), None

    return json.dumps({
        "success": True,
        "path": file_path,
        "content": file_content
    }), file_path


# Conversation history handling functions
def save_conversation_history(conversation_history):
    HISTORY_FILE.write_text(
        json.dumps(conversation_history, indent=2),
        encoding="utf-8"
    )

def load_conversation_history():
    if not HISTORY_FILE.exists():
        return []

    history_text = HISTORY_FILE.read_text(encoding="utf-8")
    try:
        return json.loads(history_text)
    except json.JSONDecodeError:
        print("모 : ( ˶°ㅁ°) !! Error loading conversation history. Starting fresh.")
        return []

def add_conversation_history(conversation_history, user, content, metadata=None):
    history = {"role": user, "content": content, "metadata": create_default_metadata()}

    if metadata:
        history["metadata"].update(metadata)

    conversation_history.append(history)
    save_conversation_history(conversation_history)

def print_conversation_history(conversation_history):
    print("모 : Conversation history:")
    for i, msg in enumerate(conversation_history):
        print(f" {i+1}. {msg.get('role', '???')}: {msg.get('content', '!!!')}")


# File History handling functions
def save_file_history(file_history, file_path, file_content):
    file_history[file_path] = file_content

def print_file_history(file_history):
    print("모 : File history:")
    for i, (file_path, file_content) in enumerate(file_history.items()):
        print(f" {i+1}. {file_path}: {file_content[:100]}...")  # Show first 100 chars

def clear_history(conversation_history, file_history):
    conversation_history.clear()
    file_history.clear()
    save_conversation_history(conversation_history)


# Token Usage handling functions
def print_usage():
    if not LOG_FILE.exists():
        print("모 : No usage log found.")
        return

    input_tokens_total = 0
    output_tokens_total = 0
    total_tokens_total = 0
    
    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                usage = log_entry.get("token_usage", {})
                input_tokens_total += usage.get("input_tokens", 0)
                output_tokens_total += usage.get("output_tokens", 0)
                total_tokens_total += usage.get("total_tokens", 0)
            except json.JSONDecodeError:
                print("모 : ( ˶°ㅁ°) !! Error reading a log entry. Skipping.")

    print(f"모 : Tokens used: {total_tokens_total} total, {input_tokens_total} input, {output_tokens_total} output")

def print_usage_log():
    if not LOG_FILE.exists():
        print("모 : No usage log found.")
        return

    print("모 : Usage log:")
    for i, line in enumerate(LOG_FILE.read_text(encoding="utf-8").splitlines(), 1):
        print(f" {i}. {line}")

def get_token_usage(response):
    usage = getattr(response, "usage", None)
    if usage:
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
            "total_tokens": getattr(usage, "total_tokens", 0)
        }
    else:
        return create_empty_token_usage()

def add_token_usage(tokens, new_tokens):
    tokens["input_tokens"] += new_tokens["input_tokens"]
    tokens["output_tokens"] += new_tokens["output_tokens"]
    tokens["total_tokens"] += new_tokens["total_tokens"]
    return tokens

def add_usage_log(event, user_input, usage, files_used=None, success=None):
    log_entry = create_default_logging()
    log_entry.update({
        "event": event,
        "user_input": user_input,
        "token_usage": usage
    })
    if files_used is not None:
        log_entry.update({"files_used": files_used})
    if success is not None:
        log_entry.update({"success": success})

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(log_entry) + "\n")


# Print functions
def print_response(answer, files_used, follow_up_questions):
    print("모 : " + answer)
    if files_used:
        print("모 : " + "Files used: " + ", ".join(files_used))
    if follow_up_questions:
        print("모 : " + "Follow-up questions:\n" + "\n".join(follow_up_questions))

def print_token_usage(token_usage):
    if token_usage:
        print(
            f"모 : Tokens used: "
            f"{token_usage['input_tokens']} input, "
            f"{token_usage['output_tokens']} output, "
            f"{token_usage['total_tokens']} total"
        )
    else: 
        print("모 : ( ╹ -╹)? Token data not found.")

# Prompt building and AI interaction functions
def build_prompt(conversation_history):
    prompt = []

    for msg in conversation_history:
        prompt.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })

    return prompt

def get_event_message(event):
    message = getattr(event, "message", None)
    if message:
        return message

    response = getattr(event, "response", None)
    if response:
        response_error = getattr(response, "error", None)
        if response_error:
            return getattr(response_error, "message", str(response_error))

        incomplete_details = getattr(response, "incomplete_details", None)
        if incomplete_details:
            return str(incomplete_details)

    return "No details provided."

def get_tool_calls(response):
    return [
        item for item in getattr(response, "output", []) or []
        if getattr(item, "type", None) == "function_call"
    ]

def response_output_to_input_items(response):
    # helper function to take the model’s previous response.output items and make them safe to include in the next input.
    input_items = []

    output_items = getattr(response, "output", []) or []

    for output_item in output_items:
        if hasattr(output_item, "model_dump"):
            input_items.append(output_item.model_dump(exclude_none=True))
        else:
            input_items.append(output_item)
    return input_items

def ask_ai_with_tools(client, model_input, file_history):
    current_input = list(model_input)
    files_used_by_tools = []
    token_usage_sum = create_empty_token_usage()

    rounds=0

    while True: 
        response_text, response = ask_ai_stream(client, current_input, tools=[READ_TEXT_FILE_TOOL])
        if not response:
            return response_text, None, files_used_by_tools, token_usage_sum
        
        token_usage_sum = add_token_usage(token_usage_sum, get_token_usage(response))
        tool_calls = get_tool_calls(response)

        if not tool_calls: 
            # No tool calls needed, returning response as-is
            return response_text, response, files_used_by_tools, token_usage_sum

        if rounds >= MAX_TOOL_CALL_ROUNDS:
            print("모 : (,; ⩌ ;,) Exceeded max tool count... does the file exist? ")
            return "", None, files_used_by_tools, token_usage_sum
        
        # append current response to the input
        current_input.extend(response_output_to_input_items(response))

        print("모 : (ᓀ‸ᓂ) Tool calls needed...")
        # make the tool calls requested by the model
        for tool_call in tool_calls:
            tool_output, file_path = execute_read_text_file_tool(
                file_history,
                tool_call.arguments
            )

            if file_path and file_path not in files_used_by_tools:
                files_used_by_tools.append(file_path)

            # add the tool response to the current input
            current_input.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": tool_output
            })
        rounds += 1

def ask_ai_stream(client, conversation_history, tools=None):
    streamed_text = ""
    final_response = None
    last_thinking_time = time.monotonic()

    try: 
        stream = client.responses.create(
            model=MODEL_NAME,
            input=conversation_history,
            tools=tools or [],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "response",
                    "strict": True,
                    "schema": ASSISTANT_RESPONSE_SCHEMA,
                }
            },
            stream=True,
        )

        print("모 : (╭ರ_•́) thinking", end="", flush=True)

        for event in stream:
            now = time.monotonic()

            if now - last_thinking_time >= 0.5:
                print(".", end="", flush=True)
                last_thinking_time = now

            if event.type == "response.output_text.delta":
                streamed_text += event.delta

            elif event.type == "response.completed":
                final_response = event.response
            elif event.type == "response.failed":
                print(f"\n모 : The model response failed. {get_event_message(event)}")
                return streamed_text, None
            elif event.type == "response.incomplete":
                print(f"\n모 : The model response was incomplete. {get_event_message(event)}")
                return streamed_text, None
            elif event.type == "error":
                print(f"\n모 : A streaming error occurred. {get_event_message(event)}")
                return streamed_text, None
        print()
        return streamed_text, final_response
    except OpenAIError as e:
        print(f"모 : ( ˶°ㅁ°) !! Something went wrong??? {e}")
        return "", None

def parse_response_text(response_text):
    return json.loads(response_text)

# Main application loop
def run_app(client):
    print("모 : Hello! I'm your AI assistant ₍₍⚞(˶>ᗜ<˶)⚟⁾⁾ Type 'exit' or 'quit' to end the conversation.")

    ## Initialize conversation history
    conversation_history = load_conversation_history()
    file_history = {}
    
    ## REPL-style loop for testing the Responses API
    try:
        while True:
            user_input = input("𖨆 : ")

            if not user_input.strip():
                continue  # Skip empty input

            if should_exit(user_input):
                print("모 : Goodbye! (˶ᵔᗜᵔ˶)ﾉﾞ")
                break
            
            if should_show_help(user_input):
                print_help()
                continue

            if should_clear(user_input):
                clear_history(conversation_history, file_history)
                print("모 : Conversation history cleared! (˶ᵔᗜᵔ˶)ﾉﾞ")
                continue
            
            if should_show_history(user_input):
                print_conversation_history(conversation_history)
                continue

            if should_show_file_history(user_input):
                print_file_history(file_history)
                continue

            if should_show_usage(user_input):
                print_usage()
                continue

            if should_show_log(user_input):
                print_usage_log()
                continue

            add_conversation_history(conversation_history, "user", user_input)
            
            # Build the prompt and ask the AI model for a response
            model_input = build_prompt(conversation_history)
            response_text, response, tool_files_used, token_usage_sum = ask_ai_with_tools(client, model_input, file_history)

            # Handle the AI model's response
            if response:
                try:
                    parsed_response = parse_response_text(response_text)
                except json.JSONDecodeError:
                    print("모 : ( ˶°ㅁ°) !! Error parsing the response. Please try again.")
                    add_usage_log("model_response_parse_error", user_input, token_usage_sum, success=False)
                    continue

                answer = parsed_response.get("answer", "No answer provided.")
                files_used = tool_files_used
                follow_up_questions = parsed_response.get("follow_up_questions", [])

                print_response(answer, files_used, follow_up_questions)
                print_token_usage(token_usage_sum)

                add_conversation_history(conversation_history, "assistant", answer, metadata={"response_output": parsed_response, "token_usage": token_usage_sum})

                add_usage_log("model_response", user_input, token_usage_sum, files_used=files_used)
            else: 
                add_usage_log("model_response_error", user_input, create_empty_token_usage(), success=False)
                print("모 : My brain shortcuited ( ꩜ ᯅ ꩜;)⁭ ⁭please try again ")
    except KeyboardInterrupt:
        print("\n모 : Goodbye! (˶ᵔᗜᵔ˶)ﾉﾞ")

def main():
    validate_openai_model()
    api_key = validate_openai_api_key()
    client = OpenAI(api_key=api_key)

    run_app(client)

if __name__ == "__main__":
    main()
