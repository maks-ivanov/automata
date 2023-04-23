import argparse
import logging
import logging.config

from spork.configs.agent_configs import AgentVersion
from spork.core.utils import get_logging_config


def update_docstrings():
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
    # logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description="Run the MrMeeseeksAgent.")
    parser.add_argument("--instructions", type=str, help="The initial instructions for the agent.")
    parser.add_argument(
        "--version",
        type=AgentVersion,
        default=AgentVersion.MEESEEKS_V1,
        help="The version of the agent.",
    )
    parser.add_argument(
        "--model", type=str, default="gpt-4", help="The model to be used for the agent."
    )
    parser.add_argument(
        "--documentation_url",
        type=str,
        default="https://python.langchain.com/en/latest",
        help="The model to be used for the agent.",
    )
    parser.add_argument(
        "--session_id", type=str, default=None, help="The session id for the agent."
    )
    parser.add_argument(
        "--stream", type=bool, default=True, help="Should we stream the responses?"
    )
    parser.add_argument(
        "--tools",
        type=str,
        default="python_indexer,python_writer,codebase_oracle",
        help="Comma-separated list of tools to be used.",
    )
    args = parser.parse_args()
    assert "python_indexer" in args.tools, "You must include the python_indexer tool."
    assert "python_writer" in args.tools, "You must include the python_writer tool."
    # inputs = {"documentation_url": args.documentation_url, "model": args.model}
    # (tool_payload, exec_tools) = load_llm_toolkits(args.tools.split(","), inputs, logger)
    # (python_indexer, _) = (tool_payload["python_indexer"], tool_payload["python_writer"])
    # overview = python_indexer.get_overview()
    # initial_payload = {"overview": overview}
    # for function in python_parser.function_dict.values():
    #     path = function.py_path
    #     raw_code = python_parser.get_raw_code(path)
    #     docstring = python_parser.get_docstring(path)
    #     if "No results found." not in docstring:
    #         continue
    #     logger.info("Prev Docstring:\n%s" % docstring)
    #     logger.info("Prev Raw Code:\n%s" % raw_code)
    #     instructions = f"The following code is located at the path {path}:\n\n{raw_code}\n\nPlease fetch the code from the raw file, then write relevant docstrings for this piece of code, and lastly, use the python-writer to write the result to disk."
    #     agent = MrMeeseeksAgent(
    #         initial_payload=initial_payload,
    #         instructions=instructions,
    #         llm_toolkits=exec_tools,
    #         version=args.version,
    #         model=args.model,
    #         session_id=args.session_id,
    #         stream=args.stream,
    #         verbose=True,
    #     )
    #     agent.run()


if __name__ == "__main__":
    update_docstrings()
