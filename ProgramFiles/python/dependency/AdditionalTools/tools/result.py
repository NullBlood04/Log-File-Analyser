from langchain.tools import tool
from ...Agents.resultAgent import ResultAgent


@tool(parse_docstring=True)
def resultAgent_prompt_node(analyse_content: str):
    """
    Analyses error content using ResultAgent AI to provide explanations.

    Args:
        analyse_content (str): Error text to analyse.

    Returns:
        str: AI-generated explanation and solution.
    """
    resultAgent = ResultAgent()
    response = resultAgent.prompt(analyse_content)
    return response
