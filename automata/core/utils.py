from github import Github

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
    """Load a YAML file.

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


def format_config_path(config_dir: str, config_path: str) -> str:
    """
    Returns the path to a config file.
    Args:
    - config_dir (str): The name of the directory the config file is in.
    - config_path (str): The name of the config file.
    Returns:
    - The path to the config file.
    """
    return os.path.join(root_path(), "automata", "configs", config_dir, config_path)


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


def compute_similarity(content_a: str, content_b: str) -> float:
    """Checks the similarity between two pieces of text using OpenAI Embeddings."""
    resp = openai.Embedding.create(
        input=[content_a, content_b], engine="text-similarity-davinci-001"
    )
    embedding_a = resp["data"][0]["embedding"]
    embedding_b = resp["data"][1]["embedding"]
    similarity = np.dot(embedding_a, embedding_b).item()
    return similarity


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


def clean_agent_result(result: str) -> str:
    """Cleans the result of an agent call."""
    result = result.split('"result_0": ')[1]
    result = result.replace("}", "")[1:-1]
    result = result.replace("\\n", "\n").strip()
    return result


def get_issue_body(issue_number: int) -> str:
    access_token = os.environ["GITHUB_API_KEY"]
    repo_name = os.environ["REPOSITORY_NAME"]
    g = Github(access_token)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(issue_number)
    return issue.body


def check_similarity(content_a: str, content_b: str) -> float:
    resp = openai.Embedding.create(
        input=[content_a, content_b], engine="text-similarity-davinci-001"
    )
    embedding_a = resp["data"][0]["embedding"]
    embedding_b = resp["data"][1]["embedding"]
    similarity = np.dot(embedding_a, embedding_b).item()
    normalized_similarity = similarity / (
        np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b)
    )
    return normalized_similarity
