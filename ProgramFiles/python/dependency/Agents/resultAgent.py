from langchain.schema import SystemMessage, HumanMessage

# Local imports
from .parent_aiConnector import Connect_AI
from AdditionalTools import (
    RESULTAGENT_SYSTEM_PROMPT,
    RESULTAGENT_HUMAN_PROMPT,
)


class ResultAgent(Connect_AI):

    system_prompt = RESULTAGENT_SYSTEM_PROMPT
    human_prompt = RESULTAGENT_HUMAN_PROMPT

    def prompt(self, error_content):  # type: ignore

        try:
            message = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=(self.human_prompt + error_content)),
            ]
            self.content = self.chat.invoke(message).content
            return self.content
        except Exception as e:
            return f"Something went Wrong: {e}"


if __name__ == "__main__":
    ai = ResultAgent()
    message = """
EventId: 1026
Source: .NET Runtime
level: Error
Time Created: 2025-07-04T10:32:15.326Z
Message: Application: MyApp.exe\nFramework Version: v4.0.30319\nDescription: The process was terminated due to an unhandled exception.\nException Info: System.NullReferenceException: Object reference not set to an instance of an object.\n   at MyApp.Program.Main(System.String[] args)
"""
    result = ai.prompt(message)
    print(result)
