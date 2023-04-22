from typing import List, Optional

import github
from langchain import LLMChain, PromptTemplate
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ReadOnlySharedMemory


class GitHubManagerAgent(Tool):
    def __init__(
        self,
        llm: ChatOpenAI,
        github_repo: github.Repository.Repository,
        memory: Optional[ReadOnlySharedMemory] = None,
    ):
        tools = build_github_tools(github_repo, llm)
        agent = initialize_agent(
            tools,
            llm=llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
        )
        super().__init__(
            name="github-manager",
            func=agent.run,
            description="A tool for performing GitHub actions. Can handle the following actions:"
            " - List issues"
            " - Create a new issue with a body."
            " - Create a pull request.",
            return_direct=True,
        )


def build_github_tools(github_repo, llm) -> List[Tool]:
    tools = [
        Tool(
            name="list-issues",
            func=lambda input_str: list_issues(github_repo),
            description="Lists all issues in the specified repository. No input necessary.",
            return_direct=False,
        ),
        Tool(
            name="create-issue",
            func=lambda input_str: create_issue(input_str, github_repo, llm),
            description="Creates a new issue with a title and body. Input: issue_body.",
            return_direct=False,
        ),
        Tool(
            name="create-pull-request",
            func=lambda input_str: create_pull_request(input_str, github_repo),
            description="Creates a pull request for an issue. Input should be issue number.",
            return_direct=False,
        ),
    ]
    return tools


def list_issues(github_repo) -> str:
    try:
        issues = github_repo.get_issues(state="all")
        result = "Issues:\n"
        for issue in issues:
            result += f"#{issue.number} - {issue.title}\n"
        return result
    except Exception as e:
        return f"Error: {e}"


def create_issue(input_str: str, github_repo, llm) -> str:
    try:
        prompt = PromptTemplate(
            template="Create concise and descriptive title for the following GitHub issue: {body}. "
            "Return the title only and nothing else.",
            input_variables=["body"],
        )
        title_chain = LLMChain(llm=llm, prompt=prompt)
        title = str(title_chain.run(input_str)).strip()
        issue = github_repo.create_issue(title=title, body=input_str)
        return f"Created issue: #{issue.number} - {issue.title}"
    except Exception as e:
        return f"Error: {e}"


def create_pull_request(input_str: str, github_repo) -> str:
    try:
        issue_number = int(input_str)
        issue = github_repo.get_issue(number=issue_number)
        current_branch = github_repo.active_branch.name
        default_branch = github_repo.get_default_branch()

        pull_request = issue.create_pull(base=default_branch, head=current_branch, issue=issue)
        return f"Created pull request: #{pull_request.number} - {pull_request.title}"
    except Exception as e:
        return f"Error: {e}"
