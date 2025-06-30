from dotenv import load_dotenv
import os

load_dotenv()

from openai import AzureOpenAI

AZURE_RESOURCE_NAME = os.getenv("AZURE_RESOURCE_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,  # type: ignore
    azure_endpoint=f"https://{AZURE_RESOURCE_NAME}.openai.azure.com/",
    api_version=AZURE_API_VERSION,
)

message = [{"role": "system", "content": "you are a helpful assistant"}]

user_name = input("Enter your name: ")
print("\nChatBot is ready! Enter 'exit' to stop")

while True:

    user_input = input(f"{user_name}: ")
    print()

    if user_input.lower() == "exit":
        break

    message.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_NAME"), messages=message  # type: ignore
    )

    reply = response.choices[0].message.content

    print("Bot: ", reply, "\n")

    message.append({"role": "assistant", "content": reply})  # type: ignore
