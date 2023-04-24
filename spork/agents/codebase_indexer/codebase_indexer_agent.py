import os

from dotenv import load_dotenv
from langchain import FAISS
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.text_splitter import CharacterTextSplitter

from spork.agents.codebase_indexer.graph_builder import (
    build_codebase_graph,
    get_codebase_tree_format,
    get_entities_with_children_by_type_format,
)

load_dotenv()


class CodebaseIndexerAgent(Tool):
    def __init__(self, llm, memory):
        graph = build_codebase_graph(os.getenv("CODEBASE_PATH"))

        directory_tree = get_codebase_tree_format(graph)
        files = get_entities_with_children_by_type_format(graph, "file")
        classes = get_entities_with_children_by_type_format(graph, "class")
        function_definitions = get_entities_with_children_by_type_format(graph, "function_define")
        function_calls = get_entities_with_children_by_type_format(graph, "function_call")

        directory_index = build_index(directory_tree, llm, memory)
        file_index = build_index(files, llm, memory)
        class_index = build_index(classes, llm, memory)
        function_definition_index = build_index(function_definitions, llm, memory)
        function_call_index = build_index(function_calls, llm, memory)

        tools = [
            Tool(
                name="Directory Content Lookup",
                func=lambda q: directory_index.run(
                    f"Provide a complete answer to this query: {q}."
                ),
                description="Useful for searching through directories and files. Input should be a fully formed question.",
            ),
            Tool(
                name="File Entity Content Lookup",
                func=lambda q: file_index.run(
                    f"Provide a complete answer to this query: {q}. Include line numbers."
                ),
                description="Useful for searching through files. Input should be a fully formed question.",
            ),
            Tool(
                name="Class Entity Content Lookup",
                func=lambda q: class_index.run(
                    f"Provide a complete answer to this query: {q}. Include line numbers."
                ),
                description="Useful for searching through classes. Input should be a fully formed question.",
            ),
            Tool(
                name="Function Definition Entity Content Lookup",
                func=lambda q: function_definition_index.run(
                    f"Provide a complete answer to this query: {q}"
                ),
                description="Useful for searching through function definitions. Input should be a fully formed question.",
            ),
            Tool(
                name="Function Call Content Lookup",
                func=lambda q: function_call_index.run(
                    f"Provide a complete answer to this query: {q}"
                ),
                description="Useful for searching through function calls. Input should be a fully formed question.",
            ),
            Tool(
                name="Raw File Content Viewer",
                func=get_raw_file_content,
                description="Useful for inspecting raw file content. Input should be a comma separated list of file path, start line, and end line.",
            ),
        ]

        agent = initialize_agent(
            tools, llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
        )

        super().__init__(
            name="Codebase Question Answerer",
            func=lambda q: agent.run(
                f"Determine if the query is about one or more of: directories, files, classes, function definitions, function calls, or variables."
                f"then use one or more of your tools to completely and thoroughly answer the query: {q}."
                f"After each question, decide if you need a follow up and use the appropriate tool to answer the follow up."
            ),
            description="Useful for searching through codebases for information about directories, functions, classes, variables, and imports. Input should be a fully formed question.",
        )


def get_raw_file_content(args_str):
    try:
        args = args_str.split(",")
        file_path = args[0]
        start = int(args[1])
        end = int(args[2])
        with open(file_path, "r") as f:
            lines = f.readlines()[start:end]
            # append line numbers to each line
            lines = [f"{i + start}: {line}" for i, line in enumerate(lines)]
            return "".join(lines)
    except Exception as e:
        return f"Error: {e}"


def build_index(content, llm, memory):
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=100, separator="\n")
    chunks = text_splitter.split_text(content)
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(chunks, embeddings)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=docsearch.as_retriever(), memory=memory
    )
    return chain


if __name__ == "__main__":
    llm = ChatOpenAI(streaming=True, temperature=0, model_name="gpt-4")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    agent = CodebaseIndexerAgent(llm, readonlymemory)
    breakpoint()
