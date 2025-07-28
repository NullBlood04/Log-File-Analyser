from langchain_openai import AzureChatOpenAI
from abc import ABC
from dotenv import load_dotenv
import os

from . import PROJECT_ROOT

load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))


class Connect_AI(ABC):

    system_prompt: str
    human_prompt: str

    # Establish Connection
    def __init__(self) -> None:
        AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
        AZURE_RESOURCE_NAME = os.getenv("AZURE_RESOURCE_NAME")
        AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
        self.chat = AzureChatOpenAI(
            azure_deployment=AZURE_DEPLOYMENT_NAME,  # type: ignore
            azure_endpoint=f"https://{AZURE_RESOURCE_NAME}.openai.azure.com/",
            api_key=AZURE_OPENAI_API_KEY,  # type: ignore
            api_version=AZURE_API_VERSION,
            temperature=0.2,
        )
