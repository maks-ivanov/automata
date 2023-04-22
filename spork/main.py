#!/usr/bin/env python3
import os
import sys
import traceback

from git import Repo
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory

# Log into GitHub
from spork.utils import login_github
from .agents.git_manager_agent import GitManagerAgent
from .agents.github_manager_agent import GithubManagerAgent
from .config import (
    DEFAULT_BRANCH_NAME,
    DO_RETRY,
    GITHUB_API_KEY,
    PLANNER_AGENT_OUTPUT_STRING,
    REPOSITORY_NAME,
)
from .prompts import make_execution_task, make_planning_task

print("Logging into github")
github_client = login_github(GITHUB_API_KEY)

github_repo = github_client.get_repo(REPOSITORY_NAME)


# create a repo object which represents the repository we are inside of
pygit_repo = Repo(os.getcwd())

# reset to default branch if necessary
if pygit_repo.active_branch.name != DEFAULT_BRANCH_NAME:
    pygit_repo.git.checkout(DEFAULT_BRANCH_NAME)


llm1 = ChatOpenAI(streaming=True, temperature=0.1, model_name="gpt-4")

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
readonlymemory = ReadOnlySharedMemory(memory=memory)

# TOOLS
git_manager = GitManagerAgent(llm1, pygit_repo, memory=readonlymemory)
github_manager = GithubManagerAgent(llm1, github_repo, memory=readonlymemory)
planning_tools = [git_manager, github_manager]

# AGENTS
plan_agent = initialize_agent(
    planning_tools,
    llm1,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
)

breakpoint()

exec_agent = initialize_agent(
    exec_tools, llm1, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

# check if instrutions are already attached to the issue
instructions_list = [
    c.body for c in work_item.get_comments() if c.body.startswith(PLANNER_AGENT_OUTPUT_STRING)
]
instructions = ""
if instructions_list:
    instructions = instructions_list.pop()
    instructions.replace(PLANNER_AGENT_OUTPUT_STRING, "")
    print("Found instructions:", instructions)

# ask user if they want to run planner agent, default is yes if no instructions

do_plan = input("Do you want to run the PLANNING agent? (y/n)")

if do_plan == "y":
    plan_task = make_planning_task(work_item, exec_tools, github_repo.name)
    print("Planning task:", plan_task)
    approved = False
    while not approved:
        instructions = plan_agent.run(plan_task)
        print("Created new Instructions:", instructions)
        feedback = input(
            "Do you approve? If approved, type 'y'. If not approved, type why so the agent can try again: "
        )
        approved = feedback == "y"
        plan_task = feedback

    # save instructions to issue
    work_item.create_comment(PLANNER_AGENT_OUTPUT_STRING + instructions)


# ask user if they want to run exec agent
do_exec = input("Do you want to run the EXECUTION agent? (y/n)")
success = False
branch_to_delete = None
if do_exec == "y":
    exec_task = make_execution_task(work_item, instructions, github_repo.name)
    print("Execution task:", exec_task)
    try:
        exec_agent.run(exec_task)
        success = True
    except ValueError as e:
        if DO_RETRY:
            tb = traceback.format_exc()
            print(f"Failed to complete execution task with {e}, traceback: {tb}")
            print("New task:", exec_task)
            print("Retrying...")
            exec_agent.run(exec_task)
            success = True
    finally:
        if not success and pygit_repo.active_branch.name != DEFAULT_BRANCH_NAME:
            branch_to_delete = pygit_repo.active_branch.name
        sys.stdout = pass_through_buffer.original_buffer
        pygit_repo.git.checkout(DEFAULT_BRANCH_NAME)
        if branch_to_delete:
            pygit_repo.git.branch("-D", branch_to_delete)
