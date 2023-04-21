Overview of code in each file and what it is meant to do
Getting started guide to run the code for new users

# Overview

Spork Code Repository

This repository contains a collection of tools and utilities for various tasks.

Main Packages and Modules:

1. spork.main_meeseeks:
   The main package for the Meeseeks project. It currently has no documentation.

2. spork.tools.prompts:
   A module containing task generators for planning and execution agents.
   Functions:

   - make_planning_task: A function for generating a planning task for an agent.
   - make_execution_task: A function for generating an execution task for an agent.

3. spork.tools.utils:
   A module providing functions to interact with the GitHub API. It includes listing repositories, issues, and pull requests, choosing a work item, and removing HTML tags from text.

4. spork.tools.python_tools.python_indexer:
   A module providing functionality to extract information about classes, functions, and their docstrings from a given directory of Python files. It defines the `PythonIndexer` class that can be used to get the source code, docstrings, and list of functions or classes within a specific file.

5. spork.tools.python_tools.python_writer:
   A module which provides the ability to change the in-memory representation of a python module in the PythonIndexer and to
   write this out to disk

6. spork.tools.documentation_tools.documentation_gpt:
   A simple chatbot that uses DocGPT to answer questions about documentation.

7. spork.tools.oracle.codebase_oracle:
   A codebase oracle module. The documentation for this module is currently unavailable.

8. spork.agents.mr_meeseeks_agent:
   MrMeeseeksAgent is an autonomous agent that performs the actual work of the Spork system. Meeseeks are responsible for executing instructions and reporting the results back to the master.

# Getting Started

To run the code, follow these steps:

1. Clone the repository on your local machine.
2. Navigate to the project directory.
3. Create and activate a virtual environment by running `python3 -m venv local_env && source local_env/bin/activate`
4. Upgrade to the latest pip by running `python3 -m pip install --upgrade pip`
5. Install the project in editable mode by running `pip3 install -e .`
6. Install pre-commit hooks by running `pre-commit install`
7. Execute the main script by running `python -m spork.main`
