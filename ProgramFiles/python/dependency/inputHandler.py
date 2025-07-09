from parent_aiConnector import Connect_AI
from langchain.schema import SystemMessage, HumanMessage
from literals import inputHandlerAgent_system_prompt
import re


class HandleInput(Connect_AI):

    system_prompt = inputHandlerAgent_system_prompt

    def prompt(self, error_content: str):  # type: ignore

        try:
            message = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=error_content),
            ]
            self.content = str(self.chat.invoke(message).content)
            pattern = re.compile(r"\{[^{}]*\}", re.DOTALL)
            matches = pattern.search(self.content)
            return matches
        except Exception as e:
            return f"Something went Wrong: {e}"
