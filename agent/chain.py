from langchain.agents import AgentExecutor, initialize_agent, load_tools
from langchain.llms import OpenAI


def get_chain() -> AgentExecutor:
    """Load the agent executor chain."""
    llm = OpenAI(temperature=0)
    tools = load_tools(["llm-math"], llm)
    return initialize_agent(tools, llm, "zero-shot-react-description")
