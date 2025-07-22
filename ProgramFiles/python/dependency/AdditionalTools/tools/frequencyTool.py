from langchain.tools import tool
from ...Agents.frequencyAgent import ErrorFrequencyAgent


@tool(parse_docstring=True)
def errorFrequencyAgent_prompt_node(timestamps: str):
    """
    Summarises error frequency from given timestamps using AI.

    Args:
        timestamps (str): Stringified list of error timestamps.

    Returns:
        str: One-line AI summary of error frequency.
    """
    print("_________________ErrorFrequency used_____________________", "\n", timestamps)
    frequencyAgent = ErrorFrequencyAgent()
    response = frequencyAgent.frequency_prompt(timestamps)
    return response
