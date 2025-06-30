from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json
from matplotlib import pyplot as plt

load_dotenv()


class FunctionCalling:

    def query_openai(self, msg, function):
        AZURE_RESOURCE_NAME = os.getenv("AZURE_RESOURCE_NAME")
        AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
        GPT_MODEL = os.getenv("AZURE_DEPLOYMENT_NAME")

        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,  # type: ignore
            azure_endpoint=f"https://{AZURE_RESOURCE_NAME}.openai.azure.com/",
            api_version=AZURE_API_VERSION,
        )

        response = client.chat.completions.create(
            model=GPT_MODEL,  # type: ignore
            messages=[{"role": "user", "content": msg}],
            tools=function,
        )

        return response


if __name__ == "__main__":
    fc = FunctionCalling()

    def graph_plot(x: list, y: list):
        """
        plots graph on the x, y plane
        """
        plt.plot(x, y)
        plt.show()

    func_name = {
        "type": "function",
        "function": {
            "name": "graph_plot",
            "description": "plots graph in x, y plane",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "list of integers to be ploted in x-axis",
                    },
                    "y": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "list of integers to be ploted in y-axis",
                    },
                },
            },
        },
    }

    with open("JSON\\functions.json", "r") as jsonFile:
        loadedFile = json.load(jsonFile)

    print(loadedFile["function1"])

    prompt_message = "Please draw the line y=10x in cartissian plane for x = 1, 2, 3"

    result = fc.query_openai(prompt_message, function=[loadedFile["function1"]])
    # print(result.choices[0].message.tool_calls[0].function)

    function_name = result.choices[0].message.tool_calls[0].function.name  # type: ignore
    function_arguments = result.choices[0].message.tool_calls[0].function.arguments  # type: ignore

    functionCalling = f"{function_name}(**{function_arguments})"

    print(functionCalling)
    exec(functionCalling)
