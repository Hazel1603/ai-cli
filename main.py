from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import sys
import re
import json
import copy

# global variable to store conversation history
HISTORY_FILE = Path("conversation_history.json")
TEXT_FILE_TYPES = {".txt", ".md", ".py", ".json", ".csv"}

def should_exit(user_input):
    return user_input.lower() in {"exit", "quit", "bye"}

def should_clear(user_input):
    return user_input.lower() in {"clear", "reset", "forget"}

def should_show_history(user_input):
    return user_input.lower() in {"history", "show history", "conversation history"}

def should_show_file_history(user_input):
    return user_input.lower() in {"file history", "show file history"}

def validate_openai_api_key():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("모 : ∘ ∘ ∘ ( °ヮ° ) ? OPENAI_API_KEY is not set. Add it to your .env file and try again! (˶ᵔᗜᵔ˶)ﾉﾞ\n")
        sys.exit(1)
    else:
        print("모 : (•̀ᴗ•́ )و OPENAI_API_KEY is set. Proceeding...\n")
        return api_key

def find_text_file_paths(user_input):
    matches = re.findall(
        r"(?:\.\/)?(?:[\w.-]+\/)*[\w.-]+\.(?:txt|md|py|json|csv)\b",
        user_input
    )

    return list(dict.fromkeys(matches))

def read_text_file(file_history, user_filename):
    if user_filename in file_history:
        print("모 : ^⎚-⎚^ Reading file from history...\n")
        return file_history[user_filename]

    path = Path(user_filename)

    if path.exists() and path.is_file() and path.suffix.lower() in TEXT_FILE_TYPES:
        print("모 : ^⎚-⎚^ Reading file...\n")
        file_content = path.read_text(encoding="utf-8")
        save_file_history(file_history, user_filename, file_content)
        return file_content
    else:
        return None

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
        print("모 : ( ˶°ㅁ°) !! Error loading conversation history. Starting fresh.\n")
        return []

def build_prompt(conversation_history, file_history):
    prompt = copy.deepcopy(conversation_history)
    included_files = []
    for msg in conversation_history:
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
            input=conversation_history
        )
        return response
    except OpenAIError as e:
        print(f"모 : ( ˶°ㅁ°) !! Something went wrong??? {e}")

def create_default_metadata():
    return {
        "timestamp": datetime.now().isoformat(),
        "used_file": False,
        "file_paths": [],
    }

def add_conversation_history(conversation_history, user, content, metadata=None):
    history = {"role": user, "content": content, "metadata": create_default_metadata()}

    if metadata:
        history["metadata"].update(metadata)

    conversation_history.append(history)
    save_conversation_history(conversation_history)

def save_file_history(file_history, file_path, file_content):
    file_history[file_path] = file_content

def run_app(client):
    print("모 : Hello! I'm your AI assistant ₍₍⚞(˶>ᗜ<˶)⚟⁾⁾ Type 'exit' or 'quit' to end the conversation.\n")

    ## Initialize conversation history
    conversation_history = load_conversation_history()
    file_history = {}
    
    ## REPL-style loop for testing the Responses API
    while True:
        user_input = input("𖨆 : ")

        ## Check for exit conditions
        if should_exit(user_input):
            print("모 : Goodbye! (˶ᵔᗜᵔ˶)ﾉﾞ")
            break
        
        if should_clear(user_input):
            conversation_history.clear()
            file_history.clear()
            save_conversation_history(conversation_history)
            print("모 : Conversation history cleared! (˶ᵔᗜᵔ˶)ﾉﾞ\n")
            continue
        
        if should_show_history(user_input):
            print("모 : Conversation history:\n")
            for i, msg in enumerate(conversation_history):
                print(f" {i+1}. {msg.get('role', '???')}: {msg.get('content', '!!!')}\n")
            continue

        if should_show_file_history(user_input):
            print("모 : File history:\n")
            for i, (file_path, file_content) in enumerate(file_history.items()):
                print(f" {i+1}. {file_path}: {file_content[:100]}...\n")  # Show first 100 chars
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
                print(f"모 : (•̀ᴗ•́ )و I found and read the following files: {', '.join(readable_file_paths)}\n")
            else:
                print("모 : ( ˶°ㅁ°) !! I couldn't read any of the specified files.\n")
                continue

            metadata = {
                "used_file": True,
                "file_paths": readable_file_paths,
            }
            add_conversation_history(conversation_history, "user", user_input, metadata=metadata)
        else :
            add_conversation_history(conversation_history, "user", user_input)
        
        model_input = build_prompt(conversation_history, file_history)
        response = ask_ai(client, model_input)

        if response:
            print("모 : " + response.output_text)
            add_conversation_history(conversation_history, "assistant", response.output_text)
        else: 
            print("모 : My brain shortcuited ( ꩜ ᯅ ꩜;)⁭ ⁭please try again \n")

def main():
    api_key = validate_openai_api_key()
    client = OpenAI(api_key=api_key)

    run_app(client)

if __name__ == "__main__":
    main()