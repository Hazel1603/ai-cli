from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from pathlib import Path
import os
import sys
import re

def should_exit(user_input):
    return user_input.lower() in {"exit", "quit", "bye"}
    
def validate_openai_api_key():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("모 : ∘ ∘ ∘ ( °ヮ° ) ? OPENAI_API_KEY is not set. Add it to your .env file and try again! (˶ᵔᗜᵔ˶)ﾉﾞ\n")
        sys.exit(1)
    else:
        print("모 : (•̀ᴗ•́ )و OPENAI_API_KEY is set. Proceeding...\n")
        return api_key

def find_text_file_path(user_input):
    match = re.search(
        r"(?:\.\/)?(?:[\w.-]+\/)*[\w.-]+\.(?:txt|md|py|json|csv)\b",
        user_input
    )
    if match:
        return match.group(0)
    return None

def read_text_file(user_filename):
    TEXT_FILE_TYPES = {".txt", ".md", ".py", ".json", ".csv"}

    path = Path(user_filename)

    if path.exists() and path.is_file() and path.suffix.lower() in TEXT_FILE_TYPES:
        return path.read_text(encoding="utf-8")
    else:
        print("모 : ( ˶°ㅁ°) !! I can't read that file.\n")
        return None

def build_file_prompt(user_input, file_path, file_content):
    return f"""
The user asked: {user_input}

Here is the content of {file_path}:

{file_content}
"""

def ask_ai(client, user_input):
    try: 
        response = client.responses.create(
            model="gpt-5.5",
            input=user_input
        )
        return response
    except OpenAIError as e:
        print(f"모 : ( ˶°ㅁ°) !! Something went wrong??? {e}")

def run_app(client):
    print("모 : Hello! I'm your AI assistant ₍₍⚞(˶>ᗜ<˶)⚟⁾⁾ Type 'exit' or 'quit' to end the conversation.\n")
    
    ## REPL-style loop for testing the Responses API
    while True:
        user_input = input("𖨆 : ")

        ## Check for exit conditions
        if should_exit(user_input):
            print("모 : Goodbye! (˶ᵔᗜᵔ˶)ﾉﾞ")
            break
        
        ## Check if the user input contains a valid text file path
        file_path = find_text_file_path(user_input)
        if file_path:
            file_content = read_text_file(file_path)

            if file_content is None:
                continue  # Skip to the next iteration if the file couldn't be read

            user_input = build_file_prompt(user_input, file_path, file_content)
        
        response = ask_ai(client, user_input)

        if response:
            print("모 : " + response.output_text)
        else: 
            print("모 : My brain shortcuited ( ꩜ ᯅ ꩜;)⁭ ⁭please try again \n")

def main():
    api_key = validate_openai_api_key()
    client = OpenAI(api_key=api_key)

    run_app(client)

if __name__ == "__main__":
    main()