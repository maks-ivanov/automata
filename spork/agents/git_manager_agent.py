from typing import List, Optional

import git
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ReadOnlySharedMemory


class GitManagerAgent(Tool):
    def __init__(
        self,
        llm: ChatOpenAI,
        pygit_repo: git.Repo,
        memory: Optional[ReadOnlySharedMemory] = None,
    ):
        tools = build_tools(pygit_repo)
        agent = initialize_agent(
            tools,
            llm=llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
        )
        super().__init__(
            name="git-manager",
            func=agent.run,
            description="A tool for performing git commands. Can handle the following actions:"
            " - List branches"
            " - Create a new branch with a name of your choice."
            " - Commit files to git and push. Specify the files you want to commit as a comma-separated list of full paths."
            " - Checkout an existing branch by name.",
            return_direct=True,
        )


def build_tools(pygit_repo) -> List[Tool]:
    tools = [
        Tool(
            name="new-branch",
            func=lambda input_str: create_new_branch(input_str, pygit_repo),
            description="Creates and checks out a new branch in the specified repository. The only input is the branch name. For example: 'my-branch'.",
            return_direct=False,
        ),
        Tool(
            name="commit",
            func=lambda input_str: commit_to_git(input_str, pygit_repo),
            description="Takes a string of comma-separated file names and commits them to git. For example: 'file1.py,file2.py'.",
            return_direct=False,
        ),
        Tool(
            name="checkout-existing-branch",
            func=lambda input_str: checkout_branch(input_str, pygit_repo),
            description="Checks out an existing branch in the specified repository. The only input is the branch name. For example: 'my-branch'.",
            return_direct=False,
        ),
        Tool(
            name="list-branches",
            func=lambda input_str: list_branches(pygit_repo),
            description="Lists all branches in the specified repository. No input necessary.",
        ),
    ]
    return tools


def create_new_branch(branch_name: str, pygit_repo) -> str:
    try:
        pygit_repo.git.branch(branch_name)
        pygit_repo.git.checkout(branch_name)
        return f"Created and checked out branch {branch_name}."
    except Exception as e:
        return f"Error: {e}"


def checkout_branch(branch_name: str, pygit_repo) -> str:
    success = f"Checked out an existing branch {branch_name}."
    try:
        pygit_repo.git.checkout(branch_name)
        try:
            pygit_repo.git.pull()
        except Exception:
            return "Note: remote branch doesn't exist, nothing to pull. " + success
        return success
    except Exception as e:
        return f"Error: {e}"


def commit_to_git(file_names: str, pygit_repo) -> str:
    try:
        file_names_list = file_names.split(",")
        for file_name in file_names_list:
            pygit_repo.git.add(file_name)

        pygit_repo.git.commit(m="Committing changes")
        pygit_repo.git.push("--set-upstream", "origin", pygit_repo.git.branch("--show-current"))
        return f"Committed {file_names}"
    except Exception as e:
        return f"Error: {e}"


def list_branches(pygit_repo) -> str:
    try:
        return pygit_repo.git.branch("-a")
    except Exception as e:
        return f"Error: {e}"
