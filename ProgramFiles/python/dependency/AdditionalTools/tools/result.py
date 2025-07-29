from langchain.tools import tool
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@tool(parse_docstring=True)
def resultAgent_prompt_node(analyse_content: str):
    """
    Analyses error content using ResultAgent AI to provide explanations.

    Args:
        analyse_content (str): Error text to analyse.

    Returns:
        str: AI-generated explanation and solution.
    """
    from ...Agents import ResultAgent

    logging.info(f"Received content for analysis: {analyse_content}")
    resultAgent = ResultAgent()
    response = resultAgent.prompt(analyse_content)
    logging.info(f"ResultAgent response: {response}")
    return response
