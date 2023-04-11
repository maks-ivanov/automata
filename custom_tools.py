from typing import List, Union, Optional

import git
import github
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository
from langchain.agents import Tool

from utils import PassThroughBuffer


class GitToolBuilder:
    def __init__(
        self,
        github_repo: github.Repository,
        pygit_repo: git.Repo,
        work_item: Union[Issue, PullRequest],
        logger: Optional[PassThroughBuffer] = None,
    ):
        # we need a github repo object to interact with the github API
        # we need pygit repo object to do actual git things
        self.github_repo = github_repo
        self.pygit_repo = pygit_repo
        self.work_item = work_item
        self.logger = logger

    def build_tools(self) -> List[Tool]:
        tools = [
            Tool(
                name="git-new-branch",
                func=lambda input_str: self.create_new_branch(input_str),
                description="Creates and checks out a new branch in the specified repository. The only input is the branch name. For exmpale: 'my-branch'",
                return_direct=False,
            ),
            Tool(
                name="git-commit",
                func=lambda input_str: self.commit_to_git(input_str),
                description="Takes a string of comma-separated file names and commits them to git. For example 'file1.py,file2.py'",
                return_direct=False,
            ),
            Tool(
                name="git-create-pull-request",
                func=lambda input_str: self.create_pull_request(input_str),
                description="Creates a pull request in the specified repository.",
                return_direct=False,
            ),
            Tool(
                name="git-checkout-existing-branch",
                func=lambda input_str: self.checkout_branch(input_str),
                description="Checks out an existing branch in the specified repository. The only input is the branch name. For exmpale: 'my-branch'",
                return_direct=False,
            ),
        ]
        return tools

    def create_new_branch(self, branch_name: str) -> str:
        """
        Creates and checks out a new branch in the specified repository. The only input is the branch name. For exmpale: "my-branch". Before creating a new branch, make sure to pick a name that is not taken."
        """
        # Create branch
        self.pygit_repo.git.branch(branch_name)
        # Checkout branch
        self.pygit_repo.git.checkout(branch_name)

        return f"Created and checked out branch {branch_name} in {self.github_repo.name} repository."

    def checkout_branch(self, branch_name: str) -> str:
        """
        Creates and checks out a new branch in the specified repository. The only input is the branch name. For exmpale: "my-branch"
        """
        # Checkout branch
        self.pygit_repo.git.checkout(branch_name)
        self.pygit_repo.git.pull()
        return f"Checked out an existing branch {branch_name} in {self.github_repo.name} repository."

    def commit_to_git(self, file_names: str) -> str:
        """
        Takes a string of comma-separated file names and commits them to git. For example "file1.py,file2.py"
        """
        file_names = file_names.split(",")
        for file_name in file_names:
            self.pygit_repo.git.add(file_name)

        self.pygit_repo.git.commit(m="Committing changes")
        self.pygit_repo.git.push(
            "--set-upstream", "origin", self.pygit_repo.git.branch("--show-current")
        )
        return f"Committed {file_names} to {self.github_repo.name} repository."

    def create_pull_request(self, body) -> str:
        """
        Creates a pull request in the specified repository.
        """
        # get current branch name
        assert type(self.work_item) == Issue
        current_branch = self.pygit_repo.git.branch("--show-current")
        title = "Fix for issue #" + str(self.work_item.number)
        pull: github.PullRequest.PullRequest = self.github_repo.create_pull(
            head=current_branch,
            base=self.github_repo.default_branch_name,
            issue=self.work_item,
        )
        if self.logger:
            pull.create_issue_comment(self.logger.saved_output)
        return (
            f"Created pull request for  {title} in {self.github_repo.name} repository."
        )


    def clone_repository(self, repository_url, repository_name):
        repo_path = os.path.join(config.WORKING_DIRECTORY, repository_name)
        if not os.path.exists(repo_path):
            git.Repo.clone_from(repository_url, repo_path)
        os.chdir(repo_path)


    def build_tools(self, build_tool_params):
        tools = super().build_tools(build_tool_params)
        tools.append(Tool(name="Clone Repository", command=self.clone_repository))
        return tools
