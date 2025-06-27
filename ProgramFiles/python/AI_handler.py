from parent_aiConnector import Connect_AI
from langchain.schema import SystemMessage, HumanMessage


class ResultAgent(Connect_AI):

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

    # Prompts AI
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
