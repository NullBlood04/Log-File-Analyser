from parent_aiConnector import Connect_AI
from langchain.schema import SystemMessage, HumanMessage
from literals import (
    resultAgent_system_prompt,
    resultAgent_human_prompt,
)


class ResultAgent(Connect_AI):

    system_prompt = resultAgent_system_prompt

    human_prompt = resultAgent_human_prompt

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
