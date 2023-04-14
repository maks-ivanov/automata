from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain.llms import BaseLLM
from langchain.memory import ReadOnlySharedMemory

from spork.tools.codebase_oracle_tool import CodebaseOracleToolBuilder
from spork.tools.diff_applier_tool import DiffApplierTool
from spork.tools.diff_writer_tool import DiffWriterTool


def make_text_editor_agent(
    llm: BaseLLM, memory: ReadOnlySharedMemory, home_dir: str
) -> AgentExecutor:
    """Create a text editor agent."""
    codebase_oracle_tool = CodebaseOracleToolBuilder(home_dir, llm, memory).build()
    diff_writer_tool = DiffWriterTool(llm)
    diff_applier_tool = DiffApplierTool()
    tools = [codebase_oracle_tool, diff_writer_tool, diff_applier_tool]
    editor_agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
    )
    return editor_agent


def make_text_editor_task(instructions: str) -> str:
    task = (
        "You are a text editor agent. Other LLM agents call you to do editing tasks on local files. You pefrom these tasks by finding the correct files,"
        f"breaking down changes into diffs and then applying them to the right files. Your current task is: {instructions}"
        f"ALWAYS begin by asking the codebase oracle tool about the file you want to edit."
        f"Keep asking the codebase oracle tool until you are confident you have the context you need."
        f"Then, ask the diff writer tool to write a diff for you."
        f"If you get an error, you should try asking the codebase oracle tool again about the file."
        f"ALWAYS end by asking the diff applier tool to apply the diff you wrote."
    )
    return task
