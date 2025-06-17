from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

class Connect_AI:

    system_prompt = """
You are an expert in analyzing Windows Event Logs.
Your task is to examine error messages provided by the user, identify the root
cause of the issue, and suggest clear, actionable solutions. When appropriate,
explain the meaning of technical terms and recommend relevant troubleshooting
steps or Microsoft documentation. Always respond in a concise, helpful,
and professional tone.
"""

    human_prompt = """
Below are the Windows Error Event Logs retrieved from the system. Please analyze
them, explain the issue in simple terms, and provide practical, step-by-step solutions
to resolve or mitigate the problem.

"""
    # Establish Connection
    def __init__(self) -> None:
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
        self.AZURE_RESOURCE_NAME = os.getenv("AZURE_RESOURCE_NAME")
        self.AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
        self.chat = AzureChatOpenAI(
                azure_deployment=self.AZURE_DEPLOYMENT_NAME,  # type: ignore
                azure_endpoint=f"https://{self.AZURE_RESOURCE_NAME}.openai.azure.com/",
                api_key=self.AZURE_OPENAI_API_KEY, # type: ignore
                api_version=self.AZURE_API_VERSION,
                temperature=0.2
            )
        
    
    def prompt(self, error_content):
        try:
            message = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=(self.human_prompt + error_content))
            ]
            self.content = self.chat(messages=message).content
            return self.content
        except Exception as e:
            return f"Something went Wrong: {e}"

    

