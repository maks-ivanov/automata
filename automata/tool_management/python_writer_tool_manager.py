import logging
from typing import List, Optional

from automata.configs.config_enums import AgentConfigName
from automata.core.base.tool import Tool
from automata.tools.python_tools.python_writer import PythonWriter

from .base_tool_manager import BaseToolManager

logger = logging.getLogger(__name__)


class PythonWriterToolManager(BaseToolManager):
    """
    PythonWriterToolManager
    A class for interacting with the PythonWriter API, which provides functionality to modify
    the code state of a given directory of Python files.
    """

    def __init__(
        self,
        **kwargs,
    ):
        """
        Initializes a PythonWriterToolManager object with the given inputs.

        Args:
        - writer (PythonWriter): A PythonWriter object representing the code writer to work with.

        Returns:
        - None
        """
        self.writer: PythonWriter = kwargs.get("python_writer")
        # TODO: unused
        self.automata_version = (
            kwargs.get("automata_version") or AgentConfigName.AUTOMATA_WRITER_PROD
        )
        self.model = kwargs.get("model") or "gpt-4"
        self.verbose = kwargs.get("verbose") or False
        self.stream = kwargs.get("stream") or True
        self.temperature = kwargs.get("temperature") or 0.7

    def build_tools(self) -> List[Tool]:
        """Builds a list of Tool object for interacting with PythonWriter."""
        tools = [
            Tool(
                name="python-writer-update-module",
                func=lambda module_object_code_tuple: self._writer_update_module(
                    *module_object_code_tuple
                ),
                description=f"Modifies the python code of a function, class, method, or module after receiving"
                f" an input module path, source code, and optional class name. If the specified object or dependencies do not exist,"
                f" then they are created automatically. If the object already exists,"
                f" then the existing code is modified."
                f" For example -"
                f' to implement a method "my_method" of "MyClass" in the module "my_file.py" which exists in "my_folder",'
                f" the correct function call follows:\n"
                f" - tool_query_1\n"
                f"   - tool_name\n"
                f"     - python-writer-update-module\n"
                f"   - tool_args\n"
                f"     - my_folder.my_file\n"
                f"     - MyClass\n"
                f'     - def my_method() -> None:\n   """My Method"""\n    print("hello world")\n'
                f"If new import statements are necessary, then introduce them at the top of the submitted input code.\n"
                f"Provide the full code as input, as this tool has no context outside of passed arguments.\n",
                return_direct=True,
            ),
        ]
        return tools

    def _writer_update_module(
        self, module_dotpath: str, class_name: Optional[str], code: str
    ) -> str:
        """Writes the given code to the given module path and class name."""
        try:
            print("Attempting to write update to module_path = ", module_dotpath)
            self.writer.update_module(
                source_code=code,
                do_extend=True,
                module_dotpath=module_dotpath,
                write_to_disk=True,
                class_name=class_name,
            )
            return "Success"
        except Exception as e:
            return "Failed to update the module with error - " + str(e)
