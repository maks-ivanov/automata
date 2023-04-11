import os
from typing import List, Union

from github.Issue import Issue
from github.PullRequest import PullRequest
from langchain.tools import BaseTool

from config import PLANNER_AGENT_OUTPUT_STRING


def make_planning_task(
    work_item: Union[Issue, PullRequest],
    exec_tools: List[BaseTool],
    github_repo_name: str,
):
    return (
        f"You are a GPT-4 software engineering lead agent."
        f" You are built with langchain, a framework for building language-based agents. "
        f" You can read about it here: https://python.langchain.com/en/latest/modules/agents.html"
        f" You are working in {os.getcwd()} on {github_repo_name} repository."
        f" Your task is to thoroughly understand the following work item and "
        f" create simple and thorough step-by-step instructions for a developer to implement the solution."
        f" <work_item> "
        f" \n\nTitle: {work_item.title}"
        f" \n\nBody: {work_item.body}"
        f" \n\nComments: {[c.body for c in work_item.get_comments() if not c.body.startswith(PLANNER_AGENT_OUTPUT_STRING)]}"
        f" </work_item> "
        f" \n\n The developer will use your instructions to make changes to the repository and"
        f" {'submit a pull request' if isinstance(work_item, Issue) else 'make a commit'}."
        f" with working, clean, and documented code."
        f" You MUST examine the existing files and their contents in the repository"
        f" before writing your output instructions."
        f" You should also look up documentation on the internet whenever necessary."
        f" Your developer is also a GPT-4 agent, so keep that in mind when creating instructions."
        f" Your output instructions should be concise and as simple as possible, but no simpler."
        f" You should tell the developer which files to create/modify/delete, and what to write in them."
        f" You should also tell the developer which external libraries to use, if any."
        f" For external libraries, you should provide a link to the documentation."
        f" You should match the existing patterns of the codebase and reuse existing code where possible."
        f" Make sure not to regress any existing functionality."
        f" The developer agent will have access to the following tools: {[(tool.name, tool.description) for tool in exec_tools]}, so keep that in mind when creating instructions."
        f" Begin."
    )


def make_execution_task(
    work_item: Union[Issue, PullRequest],
    solution_instructions: str,
    github_repo_name: str,
):
    return (
        f"You are a GPT-4-powered software engineer agent."
        f" You are built with langchain, a framework for building language-based agents. "
        f" You can read about it here: https://python.langchain.com/en/latest/modules/agents.html"
        f" Your task is to contribute clean, high-quality code to the given codebase."
        f" You are working in {os.getcwd()} on {github_repo_name} repository."
        f" You are working on the following work item: "
        f"\n\nTitle: {work_item.title};"
        f"\n\nBody: {work_item.body};"
        f"\n\nComments: {[c.body for c in work_item.get_comments() if not c.body.startswith(PLANNER_AGENT_OUTPUT_STRING)]};"
        f"\n\n A planning agent has created the following step-by-step instructions for you: <instructions>{solution_instructions}</instructions>"
        f" Execute the instructions and"
        f"{'create a pull request with your changes.' if isinstance(work_item, Issue) else 'make a commit with your changes to the appropriate branch.'}"
        f" make sure not to regress any existing functionality."
        f"\n\nUseful tips: Don't use nano, vim or other text editors, but rather modify files directly either via python or terminal. "
        f" Before creating a new branch, make sure to pick a name that is not taken."
    )
