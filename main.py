from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import sys
import re
import json

# global variable to store conversation history
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


# Text file handling functions
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
                input_tokens_total += log_entry["token_usage"]["input_tokens"]
                output_tokens_total += log_entry["token_usage"]["output_tokens"]
                total_tokens_total += log_entry["token_usage"]["total_tokens"]
            except json.JSONDecodeError:
                print("모 : ( ˶°ㅁ°) !! Error reading a log entry. Skipping.")

    print(f"모 : Tokens used: {total_tokens_total} total, {input_tokens_total} input, {output_tokens_total} output")

def print_usage_log():
    if not LOG_FILE.exists():
        return []

    logs = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        logs.append(json.loads(line))
    return logs

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
    print(
        f"모 : Tokens used: "
        f"{token_usage['input_tokens']} input, "
        f"{token_usage['output_tokens']} output, "
        f"{token_usage['total_tokens']} total"
    )


# Prompt building and AI interaction functions
def build_prompt(conversation_history, file_history):
    prompt = []
    included_files = []
    for msg in conversation_history:
        # Strip app-only metadata before sending messages to the model.
        prompt.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })
        metadata = msg.get("metadata", {})
        if msg.get("role") == "user" and metadata.get("used_file"):
            file_paths = metadata.get("file_paths", [])
            for file_path in file_paths:
                if file_path not in included_files:
                    included_files.append(file_path)

    file_context = ""
    for file_path in included_files:
        file_content = read_text_file(file_history, file_path)
        if file_content is not None:
            file_context += f"\n\nFile: {file_path}\n{file_content}"
            
    if file_context:
        prompt.insert(0, {
            "role": "developer",
            "content": f"Use this file context when answering:{file_context}"
        })
    # print(json.dumps(prompt, indent=2))
    return prompt

def ask_ai(client, conversation_history):
    try: 
        response = client.responses.create(
            model="gpt-5.5",
            input=conversation_history,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "response",
                    "strict": True,
                    "schema": ASSISTANT_RESPONSE_SCHEMA
                }
            }
        )
        return response
    except OpenAIError as e:
        print(f"모 : ( ˶°ㅁ°) !! Something went wrong??? {e}")

def parse_response(response):
    return json.loads(response.output_text)


# Main application loop
def run_app(client):
    print("모 : Hello! I'm your AI assistant ₍₍⚞(˶>ᗜ<˶)⚟⁾⁾ Type 'exit' or 'quit' to end the conversation.")

    ## Initialize conversation history
    conversation_history = load_conversation_history()
    file_history = {}
    
    ## REPL-style loop for testing the Responses API
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
            logs = print_usage_log()
            if logs:
                print("모 : Usage log:")
                for i, log in enumerate(logs):
                    print(f" {i+1}. {json.dumps(log, indent=2)}")
            else:
                print("모 : No usage log found.")
            continue

        ## Check if the user input contains a valid text file path
        file_paths = find_text_file_paths(user_input)
        if file_paths:
            readable_file_paths = []
            for file_path in file_paths:
                file_content = read_text_file(file_history, file_path)

                if file_content is not None:
                    readable_file_paths.append(file_path)
            
            if readable_file_paths:
                print(f"모 : (•̀ᴗ•́ )و I found and read the following files: {', '.join(readable_file_paths)}")
            else:
                print("모 : ( ˶°ㅁ°) !! I couldn't read any of the specified files.")
                continue

            metadata = {
                "used_file": True,
                "file_paths": readable_file_paths,
            }
            add_conversation_history(conversation_history, "user", user_input, metadata=metadata)
        else :
            add_conversation_history(conversation_history, "user", user_input)
        
        # Build the prompt and ask the AI model for a response
        model_input = build_prompt(conversation_history, file_history)
        response = ask_ai(client, model_input)

        # Handle the AI model's response
        if response:
            token_usage = get_token_usage(response)
            try:
                parsed_response = parse_response(response)
            except json.JSONDecodeError:
                print("모 : ( ˶°ㅁ°) !! Error parsing the response. Please try again.")
                add_usage_log("model_response_parse_error", user_input, token_usage, success=False)
                continue

            answer = parsed_response.get("answer", "No answer provided.")
            files_used = parsed_response.get("files_used", [])
            follow_up_questions = parsed_response.get("follow_up_questions", [])

            print_response(answer, files_used, follow_up_questions)
            print_token_usage(token_usage)

            add_conversation_history(conversation_history, "assistant", answer, metadata={"response_output": parsed_response, "token_usage": token_usage})

            add_usage_log("model_response", user_input, token_usage, files_used=files_used)
        else: 
            add_usage_log("model_response_error", user_input, create_empty_token_usage(), success=False)
            print("모 : My brain shortcuited ( ꩜ ᯅ ꩜;)⁭ ⁭please try again ")

def main():
    api_key = validate_openai_api_key()
    client = OpenAI(api_key=api_key)

    run_app(client)

if __name__ == "__main__":
    main()