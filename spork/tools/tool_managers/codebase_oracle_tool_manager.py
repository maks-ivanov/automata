from typing import List

from langchain.agents import Tool

from spork.tools.oracle.codebase_oracle import CodebaseOracle
from spork.tools.tool_managers.base_tool_manager import BaseToolManager
from spork.tools.utils import run_retrieval_chain_with_sources_format


class CodebaseOracleToolManager(BaseToolManager):
    def __init__(self, codebase_oracle: CodebaseOracle):
        self.codebase_oracle = codebase_oracle

    def build_tools(self) -> List[Tool]:
        tools = [
            Tool(
                name="codebase-oracle-agent",
                func=lambda q: run_retrieval_chain_with_sources_format(
                    self.codebase_oracle.get_chain(), q
                ),
                description="Exposes the run command a codebase oracle, which conducts a semantic search on the code repository using natural language queries, and subsequently returns the results to the master",
                return_direct=True,
                verbose=True,
            )
        ]
        return tools
