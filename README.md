
# Overview

The improved-spork project is an AI software engineering assistant that helps developers contribute clean, high-quality code to GitHub repositories. The codebase is organized into the following main components:

- **spork**: The main directory containing the core functionality of the project. It includes tools, agents, and utility functions.
- **tools**: A subdirectory within spork containing various tools such as git_tools, navigator_tool, and others.
- **agents**: A subdirectory within spork containing AI agents that interact with the tools to perform tasks.
- **scripts**: A subdirectory within spork containing the main script to run the software engineering assistant.

To get started with the project, follow the instructions in the Getting Started section below.

# Getting Started

To run the code, follow these steps:

1. Clone the repository on your local machine.
2. Navigate to the project directory.
3. Create and activate a virtual environment by running `python3 -m venv local_env && source local_env/bin/activate`
4. Upgrade to the latest pip by running `python3 -m pip install --upgrade pip`
5. Install the project in editable mode by running `pip3 install -e .`
6. Install pre-commit hooks by running `pre-commit install`
7. Execute the main script by running `python -m spork.main`
