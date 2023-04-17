"""
Parses the output of git log --numstat --graph into a networkx graph.
"""
import subprocess

import networkx as nx
import regex as re


class GitLogParser:
    def parse(cls):
        G = nx.DiGraph()
        log_output = subprocess.check_output(["git", "log", "--pretty=format:%h %p", "--numstat"])
        commit_regex = re.compile(r"^(\w+)\s(.*)$")
        file_regex = re.compile(r"^(\d+)\s+(\d+)\s+(.*)$")
        parent_commits = []
        for line in log_output.decode().split("\n"):
            match = commit_regex.match(line)
            if match:
                commit_id = match.group(1)
                parent_ids = match.group(2).split()
                G.add_node(commit_id)
                for parent_id in parent_ids:
                    if parent_id != "-":
                        G.add_edge(parent_id, commit_id)
                parent_commits = [commit_id]
            else:
                match = file_regex.match(line)
                if match:
                    added, deleted, filename = match.groups()
                    G.add_node(filename)
                    for parent_commit in parent_commits:
                        G.add_edge(parent_commit, filename, added=int(added), deleted=int(deleted))
                else:
                    parent_commits = []
