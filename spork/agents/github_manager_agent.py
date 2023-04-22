from typing import List, Optional

import github
from langchain import LLMChain, PromptTemplate
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ReadOnlySharedMemory


class GithubManagerAgent(Tool):
    def __init__(
        self,
        llm: ChatOpenAI,
        github_repo: github.Repository.Repository,
        memory: Optional[ReadOnlySharedMemory] = None,
    ):
        tools = build_tools(github_repo, llm)
        agent = initialize_agent(
            tools,
            llm=llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
        )
        super().__init__(
            name="git-hub-manager",
            func=agent.run,
            description="A tool for interacting with GitHub (***NOT GIT PROTOCOL***). Can handle the following actions:"
            " - List issues."
            " - Create a new issue. Specify the issue body."
            " - Create a new pull request in a repository. Specify issue number.",
            return_direct=True,
        )


def list_issues(github_repo):
    try:
        issues = github_repo.get_issues(state="open")
        return "\n".join([f"#{issue.number} {issue.title}" for issue in issues])
    except Exception as e:
        return f"Error: {e}"


def create_issue(input_str, github_repo, llm):
    try:
        prompt = PromptTemplate(
            input_variables=["issue_body"],
            template="What is a good title for this GitHub issue: {issue_body}? Come up with a title that captures the"
            "overall intent of the changes. Return the title only.",
        )
        title_chain = LLMChain(llm=llm, prompt=prompt)
        title = str(title_chain.run(input_str)).strip()
        issue = github_repo.create_issue(title=title, body=input_str)
        return f"Created issue #{issue.number} {issue.title}"
    except Exception as e:
        return f"Error: {e}"


def create_pull_request(input_str, github_repo):
    try:
        issue_number = int(input_str)
        current_branch = github_repo.active_branch.name
        default_branch = github_repo.default_branch
        issue = github_repo.get_issue(number=issue_number)
        pull_request = github_repo.create_pull(
            head=current_branch,
            base=default_branch,
            issue=issue,
        )
        return f"Created pull request #{pull_request.number} {pull_request.title}"
    except Exception as e:
        return f"Error: {e}"


def build_tools(github_repo, llm) -> List[Tool]:
    tools = [
        Tool(
            name="list-issues",
            func=lambda input_str: list_issues(github_repo),
            description="Lists all open issues. No input required.",
            return_direct=False,
        ),
        Tool(
            name="create-issue",
            func=lambda input_str: create_issue(input_str, github_repo, llm),
            description="Creates new issue. Specify the issue body. For example: '1. create new branch\n2. Remove the comment on line 12 from main.py'.",
            return_direct=False,
        ),
        Tool(
            name="create-pull-request",
            func=lambda input_str: create_pull_request(input_str, github_repo),
            description="Creates new pull request. Specify the issue number. For example: '123'.",
            return_direct=False,
        ),
    ]
    return tools
