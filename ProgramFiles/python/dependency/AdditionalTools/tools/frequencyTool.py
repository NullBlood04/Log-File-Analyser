from langchain.tools import tool
from ...Agents.frequencyAgent import ErrorFrequencyAgent
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@tool(parse_docstring=True)
def errorFrequencyAgent_prompt_node(timestamps: str):
    """
    Summarises error frequency from given timestamps using AI.

    Args:
        timestamps (str): Stringified list of error timestamps.

    Returns:
        str: One-line AI summary of error frequency.
    """

    logging.info(f"Received timestamps for frequency analysis: {timestamps}")
    frequencyAgent = ErrorFrequencyAgent()
    response = frequencyAgent.frequency_prompt(timestamps)
    logging.info(f"ErrorFrequencyAgent response: {response}")
    return response
