from langchain.llms import BaseLLM
from langchain.memory import ReadOnlySharedMemory

from spork.tools.oracles.documentation_oracle import DocumentationOracleTool

URL = "https://git-scm.com/docs"


class GitDocumentationOracleTool(DocumentationOracleTool):
    def __init__(self, llm: BaseLLM, memory: ReadOnlySharedMemory):
        super().__init__(
            llm=llm,
            memory=memory,
            url=URL,
            name="Git Documentation Oracle",
            description="Use this tool to ask questions about how git works and how to use it. "
            "You can ask about repositories, commits, trees, merges, pull requests, and other git concepts. "
            "You can also ask for code and command examples. Input should be a fully formed question.",
        )
