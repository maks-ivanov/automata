#!/usr/bin/env python3
import sys
import traceback

from git import Repo
from langchain.agents import initialize_agent, load_tools, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from config import *
from custom_tools import GitToolBuilder
from prompts import make_planning_task, make_execution_task
from utils import login_github, list_repositories, choose_work_item, PassThroughBuffer

# Log into GitHub
print("Logging into github")
github_client = login_github(GITHUB_API_KEY)

# List repositories

repositories = list_repositories(github_client)
print("Found recent repos:", repositories)
# Let user choose a repository
repository_name = input("Enter the name of the repository you want to work with:")

github_repo = github_client.get_repo(repository_name)


# create a repo object which represents the repository we are inside of
pygit_repo = Repo(os.getcwd())

default_branch_name = "babyagi-architecture"
# reset to default branch if necessary
if pygit_repo.active_branch.name != default_branch_name:
    pygit_repo.git.checkout(default_branch_name)

pygit_repo.git.pull()

work_item = choose_work_item(github_repo)


llm = ChatOpenAI(temperature=0, model="gpt-4")
# llm1 = OpenAI(temperature=0)
pass_through_buffer = PassThroughBuffer(sys.stdout)
assert pass_through_buffer.saved_output == ""
sys.stdout = pass_through_buffer
base_tools = load_tools(["python_repl", "terminal", "serpapi", "requests_get"], llm=llm)
exec_tools = (
    base_tools + GitToolBuilder(github_repo, pygit_repo, work_item).build_tools()
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


plan_agent = initialize_agent(
    base_tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
)

exec_agent = initialize_agent(
    exec_tools, llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

# check if instrutions are already attached to the issue
instructions = [
    c.body
    for c in work_item.get_comments()
    if c.body.startswith(PLANNER_AGENT_OUTPUT_STRING)
]
if instructions:
    instructions = instructions.pop()
    instructions.replace(PLANNER_AGENT_OUTPUT_STRING, "")
    print("Found instructions:", instructions)

# ask user if they want to run planner agent
do_plan = input("Do you want to run the planner agent? (y/n)")

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
do_exec = input("Do you want to run the execution agent? (y/n)")
if do_exec == "y":
    exec_task = make_execution_task(work_item, instructions, github_repo.name)
    print("Execution task:", exec_task)
    try:
        exec_agent.run(exec_task)
    except ValueError as e:
        if DO_RETRY:
            tb = traceback.format_exc()
            exec_task += f" This is your second attempt. During the previous attempt, you crashed with the following sequence: <run>{pass_through_buffer.saved_output}</run> Let's try again, avoiding previous mistakes."
            pass_through_buffer.saved_output = ""
            print("Failed to complete execution task")
            print("New task:", exec_task)
            print("Retrying...")
            exec_agent.run(exec_task)
    finally:
        sys.stdout = pass_through_buffer.original_buffer
        pygit_repo.git.checkout(default_branch_name)
