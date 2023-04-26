import subprocess
import webbrowser

import git
from github import Github

from automata.config import GITHUB_API_KEY, REPOSITORY_NAME, REPOSITORY_PATH

"This module provides functions to interact with the GitHub API, specifically to list repositories, issues, and pull requests,\nchoose a work item to work on, and remove HTML tags from text."
import logging
import os
from typing import Any, List

import colorlog
import numpy as np
import openai
import yaml
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain
from langchain.document_loaders import TextLoader
from langchain.schema import Document


def load_yaml(file_path: str) -> Any:
    """
    Loads a YAML file.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        Any: The content of the YAML file as a Python object.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def root_py_path() -> str:
    """
    Returns the path to the root of the project python code.

    Returns:
    - A path object in string form

    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_folder = os.path.join(script_dir, "..")
    return data_folder


def root_path() -> str:
    """
    Returns the path to the root of the project directory.

    Returns:
    - A path object in string form

    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_folder = os.path.join(script_dir, "..", "..")
    return data_folder


def get_logging_config(log_level=logging.INFO) -> dict:
    """Returns logging configuration."""
    color_scheme = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": colorlog.ColoredFormatter,
                "format": "%(log_color)s%(levelname)s:%(name)s:%(message)s",
                "log_colors": color_scheme,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
                "level": log_level,
            }
        },
        "root": {"handlers": ["console"], "level": log_level},
    }
    return logging_config


def run_retrieval_chain_with_sources_format(
    chain: BaseConversationalRetrievalChain, q: str
) -> str:
    """Runs a retrieval chain and formats the result with sources.

    Args:
        chain (BaseConversationalRetrievalChain): The retrieval chain to run.
        q (str): The query to pass to the retrieval chain.

    Returns:
        str: The formatted result containing the answer and sources.
    """
    result = chain(q)
    return f"Answer: {result['answer']}.\n\n Sources: {result.get('source_documents', [])}"


def calculate_similarity(content_a: str, content_b: str) -> float:
    resp = openai.Embedding.create(
        input=[content_a, content_b], engine="text-similarity-davinci-001"
    )
    embedding_a = resp["data"][0]["embedding"]
    embedding_b = resp["data"][1]["embedding"]
    similarity = np.dot(embedding_a, embedding_b).item()
    norm_a = np.linalg.norm(embedding_a)
    norm_b = np.linalg.norm(embedding_b)
    normalized_similarity = similarity / (norm_a * norm_b)
    return normalized_similarity


class NumberedLinesTextLoader(TextLoader):
    def load(self) -> List[Document]:
        """Load from file path."""
        with open(self.file_path, encoding=self.encoding) as f:
            lines = f.readlines()
            text = f"{self.file_path}"
            for i, line in enumerate(lines):
                text += f"{i}: {line}"
        metadata = {"source": self.file_path}
        return [Document(page_content=text, metadata=metadata)]


_github_client = Github(GITHUB_API_KEY)
_github_repo_obj = _github_client.get_repo(REPOSITORY_NAME)
_local_repo_obj = git.Repo(REPOSITORY_PATH)


def get_issue_body(issue_number: int) -> str:
    """Get the body of an issue from the GitHub API.

    Args:
        issue_number (int): The number of the issue.
    """
    issue = _github_repo_obj.get_issue(issue_number)
    return issue.body


def create_branch(branch_name: str) -> str:
    """Create and checkout a new branch using the GitPython library.

    Args:
        branch_name (str): The name of the new branch.
    """
    _local_repo_obj.git.branch(branch_name)
    return f"Created branch {branch_name}."


def checkout_branch(branch_name: str) -> str:
    """Checkout a branch using the GitPython library.

    Args:
        branch_name (str): The name of the branch to checkout.
    """
    _local_repo_obj.git.checkout(branch_name)
    return f"Checked out branch {branch_name}."


def create_pull_request(base: str, head: str, issue_number: int):
    """Create a pull request using the GitHub API.

    Args:
        base (str): The base branch of the pull request.
        head (str): The head branch of the pull request.
        issue_number (int): The number of the issue the pull request is for.
    """
    issue = _github_repo_obj.get_issue(issue_number)
    pr = _github_repo_obj.create_pull(base=base, head=head, issue=issue)
    webbrowser.open(pr.html_url)
    return f"Created pull request for issue #{issue_number} - {pr.html_url}."


def rollback(base, head):
    """
    Roll back changes, checks out base, deletes head
    """
    _local_repo_obj.git.reset("--hard")
    _local_repo_obj.git.checkout(base)
    _local_repo_obj.git.branch("-D", head)
    return f"Rolled back changes, checked out {base}, deleted {head}."


def get_current_branch() -> str:
    """Get the name of the current branch."""
    return _local_repo_obj.active_branch.name


def validate_work_branch(work_branch: str) -> bool:
    """Validate that the work branch is in the correct format."""
    current_branch = get_current_branch()
    repo = git.Repo(REPOSITORY_PATH)
    if current_branch == work_branch:
        raise ValueError(f"Work branch {work_branch} cannot be the same as the current branch.")
    if work_branch in [branch.name for branch in repo.branches]:
        raise ValueError(f"Work branch {work_branch} already exists.")
    return True


def submit(base, issue_number):
    """Commit changes and open a PR"""
    work_branch = get_current_branch()
    subprocess.run("pre-commit run --all-files", shell=True)
    _local_repo_obj.git.add("-A")
    _local_repo_obj.git.commit("-m", f"Work for issue #{issue_number}", "--no-verify")
    _local_repo_obj.git.push("origin", work_branch)
    return create_pull_request(base, work_branch, issue_number)
