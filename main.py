from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import sys

def validateOpenAIKey():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("모 : ∘ ∘ ∘ ( °ヮ° ) ? OPENAI_API_KEY is not set. Add it to your .env file and try again! (˶ᵔᗜᵔ˶)ﾉﾞ\n")
        sys.exit(1)
    else:
        print("모 : (•̀ᴗ•́ )و OPENAI_API_KEY is set. Proceeding...\n")
        return api_key

def ask_ai(client, user_input):
    try: 
        response = client.responses.create(
            model="gpt-5.5",
            input=user_input
        )
        return response
    except OpenAIError as e:
        print(f"모 : ( ˶°ㅁ°) !! Something went wrong??? {e}")

def runApp(client):
    print("모 : Hello! I'm your AI assistant ₍₍⚞(˶>ᗜ<˶)⚟⁾⁾ Type 'exit' or 'quit' to end the conversation.\n")
    
    ## REPL-style loop for testing the Responses API
    while True:
        user_input = input("𖨆 : ")

        if user_input.lower() == 'exit' or user_input.lower() == 'quit' or user_input.lower() == 'bye':
            print("모 : Goodbye! (˶ᵔᗜᵔ˶)ﾉﾞ")
            break

        response = ask_ai(client, user_input)

        if response:
            print("모 : " + response.output_text)
        else: 
            print("모 : My brain shortcuited ( ꩜ ᯅ ꩜;)⁭ ⁭please try again \n")

def main():
    api_key = validateOpenAIKey()
    client = OpenAI(api_key=api_key)

    runApp(client)

if __name__ == "__main__":
    main()