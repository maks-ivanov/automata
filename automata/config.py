"""Configuration file for the program.

This file defines environment variables that are used by the program to interact with various APIs, as well as constants that are used throughout the program.

Environment variables:
- OPENAI_API_KEY: The API key for the OpenAI API.
- GITHUB_API_KEY: The API key for the GitHub API.
- REPOSITORY_NAME: The name of the repository to use for the GitHub API.
- REPOSITORY_PATH: The path to the repository to use for the Git.

Note that the environment variables are loaded from a .env file using the `load_dotenv()` function from the `dotenv` library.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Define environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY", "")
REPOSITORY_NAME = os.getenv("REPOSITORY_NAME", "")
REPOSITORY_PATH = os.getenv("REPOSITORY_PATH", "")
CONVERSATION_DB_NAME = os.getenv("CONVERSATION_DB_NAME", "interactions.sqlite3")
