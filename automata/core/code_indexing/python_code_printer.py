import os
from contextlib import contextmanager
from typing import List, Optional, Set

from redbaron import RedBaron

from automata.core.code_indexing.python_ast_indexer import PythonASTIndexer
from automata.core.code_indexing.python_ast_navigator import PythonASTNavigator
from automata.core.code_indexing.python_code_inspector import PythonCodeInspector
from automata.core.search.symbol_graph import SymbolGraph
from automata.core.search.symbol_types import Descriptor, Symbol, SymbolReference
from automata.core.search.symbol_utils import convert_to_fst_object, get_rankable_symbols
from automata.core.utils import root_py_path


class CodePrinterConfig:
    def __init__(
        self,
        spacer: str = "  ",
        max_dependency_print_depth: int = 2,
        max_recursion_depth: int = 1,
        nearest_symbols_count: int = 5,
    ):
        self.spacer = spacer
        self.nearest_symbols_count = nearest_symbols_count
        self.max_dependency_print_depth = max_dependency_print_depth
        self.max_recursion_depth = max_recursion_depth


class CodePrinter:
    def __init__(
        self,
        graph: SymbolGraph,
        config: CodePrinterConfig = CodePrinterConfig(),
        indexer: Optional[PythonASTIndexer] = None,
    ):
        self.graph = graph
        self.config = config
        self.indexer = indexer or PythonASTIndexer.cached_default()
        self.indent_level = 0
        self.reset()

    @contextmanager
    def IndentManager(self):
        self.indent_level += 1
        yield
        self.indent_level -= 1

    def reset(self) -> None:
        self.message = ""
        self.obs_symbols: Set[Symbol] = set([])
        self.global_level = 0

    def process_message(self, message: str):
        def indent() -> str:
            return self.config.spacer * self.indent_level

        self.message += "\n".join([f"{indent()}{ele}" for ele in message.split("\n")]) + "\n"

    def process_symbol(
        self,
        symbol: Symbol,
        ranked_symbols: List[Symbol] = [],
    ) -> None:
        self.obs_symbols.add(symbol)
        if self._is_top_level():
            self.print_directory_structure(symbol)
        self.process_headline(symbol)
        if self.indent_level <= self.config.max_dependency_print_depth:  # self._is_top_level():
            with self.IndentManager():
                self.process_class(symbol)
                if self.indent_level <= self.config.max_recursion_depth:
                    self.process_dependencies(symbol)
                    self.process_nearest_symbols(ranked_symbols)
                    self.process_callers(symbol)

    def process_headline(self, symbol: Symbol) -> None:
        if self._is_top_level():
            self.process_message(f"Processing Symbol -\n{symbol.path} -\n")
        else:
            self.process_message(f"{symbol.path}\n")

    def print_directory_structure(self, symbol: Symbol) -> None:
        self.process_message(f"Local Directory Structure:")
        with self.IndentManager():
            symbol_path = str(symbol.path).replace(".", os.path.sep)
            dir_path = os.path.join(root_py_path(), "..", symbol_path)
            while not os.path.isdir(dir_path):
                dir_path = os.path.dirname(dir_path)
            overview = PythonASTIndexer.build_repository_overview(dir_path)
            self.process_message(f"{overview}\n")

    def process_class(self, symbol: Symbol) -> None:
        try:
            ast_object = convert_to_fst_object(symbol)
        except Exception as e:
            print(f"Error {e} while converting symbol {symbol.descriptors[-1].name}.")
            return None

        def process_variables(ast_object: RedBaron) -> None:
            assignments = ast_object.find_all("assignment")
            if len(assignments) > 0:
                self.process_message(f"Variables:")
            with self.IndentManager():
                for assignment in assignments:
                    if assignment.parent == ast_object:
                        self.process_message(
                            f"{str(assignment.target.dumps())}={str(assignment.value.dumps())}"
                        )
                self.process_message("")

        def process_methods(ast_object: RedBaron) -> None:
            methods = sorted(ast_object.find_all("DefNode"), key=lambda x: x.name)
            if len(methods) > 0:
                self.process_message(f"Methods:")
            with self.IndentManager():
                for method in methods:
                    self.process_method(method)

        process_variables(ast_object)
        process_methods(ast_object)

    def process_method(self, method: RedBaron, detailed: bool = False) -> None:
        if CodePrinter._is_private_method(method):
            return

        # If the method is nested, we only want to print the method signature
        # e.g. for dependencies and nearby symbols
        if self._is_within_second_call():  # e.g. a dependency or related symbol
            method_definition = f"{method.name}({method.arguments.dumps()})"
            return_annotation = (
                method.return_annotation.dumps() if method.return_annotation else "None"
            )
            self.process_message(f"{method_definition} -> {return_annotation}\n")
        # Otherwise, we want to print the entire method
        elif self._is_within_top_call():  # e.g. top level
            for code_line in method.dumps().split("\n"):
                self.process_message(code_line)

    def process_dependencies(self, symbol: Symbol) -> None:
        if self._is_top_level():
            self.process_message("Dependencies:")
            with self.IndentManager():
                all_dependencies = list(self.graph.get_symbol_dependencies(symbol))
                filtered_dependencies = get_rankable_symbols(all_dependencies)
                for dependency in filtered_dependencies:
                    if not CodePrinter._is_class(dependency):
                        continue
                    if dependency == symbol:
                        continue
                    if (
                        "automata" not in dependency.uri
                    ):  # TODO - Make this cleaner in case "automata" is not the key URI
                        continue
                    self.process_symbol(dependency)

    def process_callers(self, symbol: Symbol) -> None:
        if self.indent_level < 2:
            self.process_message(f"Callers:")
        else:
            self.process_message(f"Caller Callers:")

        with self.IndentManager():
            all_potential_callers = list(self.graph.get_potential_symbol_callers(symbol))

            def find_call(caller: SymbolReference) -> Optional[RedBaron]:
                module = convert_to_fst_object(caller.symbol)
                line_number = caller.line_number
                column_number = caller.column_number + len(symbol.descriptors[-1].name)
                return PythonASTNavigator.find_method_call_by_location(
                    module, line_number, column_number
                )

            for caller in all_potential_callers:
                call = find_call(caller)
                if call is None:
                    continue

                self.process_message(str(caller.symbol.path))

                # Call a level deeper when we encounter a factory or builder
                if "Factory" in str(caller.symbol.path) or "Builder" in str(caller.symbol.path):
                    self.process_callers(caller.symbol)

                with self.IndentManager():
                    call_parent = call.parent if call is None else None  # type: ignore
                    if call_parent is None:
                        continue
                    self.process_message(str(call_parent.dumps()))

    def process_nearest_symbols(
        self,
        search_list: List[Symbol],
    ) -> None:
        self.process_message("Closely Related Symbols:")
        with self.IndentManager():
            if len(search_list) > 0:
                printed_nearby_symbols = 0
                for ranked_symbol in search_list:
                    if printed_nearby_symbols >= self.config.nearest_symbols_count:
                        break
                    if ranked_symbol.symbol_kind_by_suffix() != Descriptor.PythonKinds.Class:
                        continue
                    elif ranked_symbol in self.obs_symbols:
                        continue
                    else:
                        printed_nearby_symbols += 1
                        self.process_symbol(ranked_symbol)

    def _is_top_level(self) -> bool:
        return self.indent_level == 0

    def _is_within_top_call(self) -> bool:
        return self.indent_level == 2

    def _is_within_second_call(self) -> bool:
        return self.indent_level == 4

    @staticmethod
    def _is_private_method(ast_object):
        return ast_object.name[0] == "_" and ast_object.name[1] != "_"

    @staticmethod
    def _is_class(symbol):
        return symbol.symbol_kind_by_suffix() == Descriptor.PythonKinds.Class

    @staticmethod
    def _get_docstring(ast_object):
        raw_doctring = PythonCodeInspector._get_docstring(ast_object).split("\n")
        return "\n".join([ele.strip() for ele in raw_doctring]).strip()
