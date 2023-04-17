from typing import List, Optional

from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain.llms import BaseLLM
from langchain.memory import ReadOnlySharedMemory

from spork.tools.oracles.git_documentation_oracle_tool import GitDocumentationOracleTool


def make_text_editor_agent(
    llm: BaseLLM, memory: ReadOnlySharedMemory, home_dir: str, callbacks: Optional[List] = None
) -> AgentExecutor:
    """Create a git manager agent to do all things git"""
    git_documentation_oracle_tool = GitDocumentationOracleTool(llm, memory)
    # the idea here is that editor changes the file, so it should call a callback for the codebase oracle to update its state
    tools = [git_documentation_oracle_tool]
    editor_agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
    )
    return editor_agent


def make_git_manager_task(instructions: str) -> str:
    task = (
        "You are a git manager. You help other agents with git protocol, and also with the git history of the specific repo. "
        "You can answer questions about how to use git, and also about the history of the repo. "
        f"Your other primary task is to execute git commands on behalf of other agents. "
        "You should use git documentation oracle to ask and answer questions about how to use git. "
        "You should use git history oracle to ask and answer questions about the history and state of the repo. "
        "Finally, you can use git command executor to execute git commands to fulfill the instructions. "
        f"Your current instructions are: {instructions}"
        "ALWAYS start out by using the oracles to ask questions related to your instructions."
        "If you see an Error, you should try asking more questions to get more context before retrying."
    )
    return task
