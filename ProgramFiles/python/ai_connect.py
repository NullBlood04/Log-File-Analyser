from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class Connect_AI:
    
    def __init__(self) -> None:
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
        self.AZURE_RESOURCE_NAME = os.getenv("AZURE_RESOURCE_NAME")
        self.AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

    def connect(self):
        chat = AzureChatOpenAI(
                azure_deployment=self.AZURE_DEPLOYMENT_NAME,  # type: ignore
                azure_endpoint=f"https://{self.AZURE_RESOURCE_NAME}.openai.azure.com/",
                api_key=self.AZURE_OPENAI_API_KEY, # type: ignore
                api_version=self.AZURE_API_VERSION,
                temperature=0.2
            )
        return chat

if __name__ == "__main__":
    Connect_AI()
    

