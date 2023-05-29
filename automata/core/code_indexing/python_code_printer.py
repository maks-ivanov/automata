from enum import Enum
from typing import Dict, List, Optional, Tuple

from redbaron import RedBaron

from automata.core.code_indexing.python_code_inspector import PythonCodeInspector
from automata.core.search.symbol_graph import SymbolGraph
from automata.core.search.symbol_types import Descriptor, Symbol
from automata.core.search.symbol_utils import convert_to_fst_object, get_rankable_symbols


class CodePrinter:
    class PrintDepth(Enum):
        TOP_LEVEL = 0
        DEPENDENCY = 1
        NEARBY = 2

    def __init__(
        self,
        graph: SymbolGraph,
        spacer: str = "  ",
    ):
        self.graph = graph
        self.spacer = spacer

        self.reset()

    def reset(self) -> None:
        self.message = ""
        self.obs_symbols = set([])
        self.global_level = 0

    def process_message(self, message: str, depth: PrintDepth):
        def indent(depth: CodePrinter.PrintDepth) -> str:
            return self.spacer * (
                (1 if depth != CodePrinter.PrintDepth.TOP_LEVEL else 0) + self.global_level
            )

        self.message += "\n".join([f"{indent(depth)}{ele}" for ele in message.split("\n")]) + "\n"

    def process_symbol(
        self,
        symbol: Symbol,
        processing_depth: PrintDepth = PrintDepth.TOP_LEVEL,
        symbols_to_context_ranks: Optional[List[Tuple[Symbol, float]]] = None,
    ) -> None:
        if processing_depth == CodePrinter.PrintDepth.TOP_LEVEL:
            self.reset()
        try:
            ast_object = convert_to_fst_object(symbol)
        except Exception as e:
            print(f"Error {e} while converting symbol {symbol.descriptors[-1].name}.")
            return None
        self.obs_symbols.add(symbol)
        self.process_headline(symbol, processing_depth)
        self.process_methods(symbol, ast_object, processing_depth)
        self.process_dependencies(symbol, processing_depth)
        if symbols_to_context_ranks:
            self.process_nearest_symbols(symbols_to_context_ranks, processing_depth)

    def process_headline(self, symbol: Symbol, processing_depth: PrintDepth) -> None:
        self.process_message(f"{symbol.path} --\n", processing_depth)

    def process_methods(
        self, symbol: Symbol, ast_object: RedBaron, processing_depth: PrintDepth
    ) -> None:
        methods = sorted(ast_object.find_all("DefNode"), key=lambda x: x.name)
        for method in methods:
            self.process_method(method, processing_depth)

    def process_method(self, method: RedBaron, processing_depth: PrintDepth) -> None:
        if CodePrinter._is_private_method(method):
            return
        # If the method is nested, we only want to print the method signature
        # e.g. for dependencies and nearby symbols
        if processing_depth != CodePrinter.PrintDepth.TOP_LEVEL:
            method_definition = f"{method.name}({method.arguments.dumps()})"
            return_annotation = (
                method.return_annotation.dumps() if method.return_annotation else "None"
            )
            self.process_message(f"{method_definition} -> {return_annotation}\n", processing_depth)
        # Otherwise, we want to print the entire method
        else:
            for code_line in method.dumps().split("\n"):
                self.process_message(code_line, processing_depth)

    def process_dependencies(self, symbol: Symbol, processing_depth: PrintDepth):
        if processing_depth.TOP_LEVEL == processing_depth:
            self.process_message("Dependencies:", processing_depth)
            all_dependencies = list(self.graph.get_symbol_dependencies(symbol))
            filtered_dependencies = get_rankable_symbols(all_dependencies)
            for dependency in filtered_dependencies:
                if not CodePrinter._is_class(dependency):
                    continue
                if dependency == symbol:
                    continue
                if "automata" not in dependency.uri:
                    continue
                self.process_symbol(dependency, CodePrinter.PrintDepth.DEPENDENCY)

    def process_nearest_symbols(
        self,
        ranked_search_results: List[Tuple[Symbol, float]],
        processing_depth: PrintDepth,
        n_symbols: int = 5,
    ):
        self.process_message("Nearest Symbols:", processing_depth)
        printed_nearby_symbols = 0
        for ranked_symbol, rank in ranked_search_results:
            if printed_nearby_symbols >= n_symbols:
                break
            if ranked_symbol.symbol_kind_by_suffix() != Descriptor.PythonKinds.Class:
                continue
            elif ranked_symbol in self.obs_symbols:
                continue
            else:
                printed_nearby_symbols += 1
                # self.obs_symbols.add(symbol)
                self.process_symbol(ranked_symbol, CodePrinter.PrintDepth.NEARBY)

    def process_target_symbols(
        self,
        symbols_to_context_ranks: Dict[Symbol, List[Tuple[Symbol, float]]],
        available_symbols: List[Symbol],
    ):
        for target_symbol in symbols_to_context_ranks.keys():
            for symbol in available_symbols:
                if symbol == target_symbol:
                    self.process_symbol(
                        symbol,
                        CodePrinter.PrintDepth.TOP_LEVEL,
                        symbols_to_context_ranks[target_symbol],
                    )

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


# class CodePrinter:
#     def __init__(
#         self,
#         graph: SymbolGraph,
#         spacer: str = "  ",
#         verbosity: int = 1,
#         max_overview_depth: int = 1,
#         max_dependency_depth: int = 0,
#     ):
#         self.graph = graph
#         self.spacer = spacer
#         self.verbosity = verbosity
#         self.max_overview_depth = max_overview_depth
#         self.max_dependency_depth = max_dependency_depth

#         self.reset()

#     def reset(self) -> None:
#         self.message = ""
#         self.obs_symbols = set([])
#         self.global_level = 0

#     def process_message(self, message: str, local_level: int):
#         def indent(local_level: int) -> str:
#             return self.spacer * (local_level + self.global_level)

#         self.message += "\n".join([f"{indent(local_level)}{ele}" for ele in message.split("\n")]) + "\n"

#     def process_symbol(self, symbol: Symbol, local_depth=0) -> None:
#         if local_depth > self.max_overview_depth:
#             self.process_message(str(symbol.path), local_depth)
#             return None
#         if local_depth == 0:
#             self.reset()
#         try:
#             ast_object = convert_to_fst_object(symbol)
#         except Exception as e:
#             print(f"Error {e} while converting symbol {symbol.descriptors[-1].name}.")
#             return None

#         self.process_headline(symbol, local_depth)
#         self.process_methods(symbol, ast_object, local_depth)
#         self.process_dependencies(symbol, local_depth)
#         # self.process_nearest_symbols(symbol)

#     def process_headline(self, symbol: Symbol, local_depth=0) -> None:
#         self.process_message(f"{symbol.path} --\n", local_depth)

#     def process_methods(self, symbol: Symbol, ast_object: RedBaron, local_depth: int) -> None:
#         methods = sorted(ast_object.find_all("DefNode"), key=lambda x: x.name)
#         for method in methods:
#             print("ZZZzzzZZZ")
#             self.process_method(method, local_depth)

#     def process_method(self, method: RedBaron, local_depth: int) -> None:
#         if CodePrinter._is_private_method(method):
#             return
#         for code_line in method.dumps().split("\n"):
#             self.process_message(code_line, local_depth + 1)

#     def process_dependencies(self, symbol: Symbol, local_depth: int):
#         self.process_message("Dependencies:", local_depth)
#         all_dependencies = list(self.graph._get_symbol_dependencies(symbol))
#         filtered_dependencies = get_rankable_symbols(all_dependencies)
#         for dependency in filtered_dependencies:
#             if not CodePrinter._is_class(dependency):
#                 continue
#             if dependency == symbol:
#                 continue
#             if 'automata' not in dependency.uri:
#                 continue
#             print("I should be processing dependency = ", symbol)
#             if local_depth < self.max_dependency_depth:
#                 self.process_symbol(dependency, local_depth + 1)
#             else:
#                 self.process_message(str(dependency.path)+"\n", local_depth + 1)
#                 self.process_symbol(dependency, local_depth + 1)

#     def process_target_symbols(self, target_symbols: List[str], ranked_symbols_list: List[List[Tuple[Symbol, float]]]):
#         for target_symbol, ranked_symbols in zip(target_symbols, ranked_symbols_list):
#             for symbol, rank in ranked_symbols:
#                 selected_symbol = False
#                 for target_symbol in target_symbols:
#                     if symbol.uri.endswith(target_symbol):
#                         selected_symbol = True
#                 if not selected_symbol:
#                     continue
#                 self.process_symbol(symbol)

#     @staticmethod
#     def _is_private_method(ast_object):
#         return ast_object.name[0] == "_" and ast_object.name[1] != "_"

#     @staticmethod
#     def _is_class(symbol):
#         return symbol.symbol_kind_by_suffix() == Descriptor.PythonKinds.Class

#     @staticmethod
#     def _get_docstring(ast_object):
#         raw_doctring = PythonCodeInspector._get_docstring(ast_object).split("\n")
#         return "\n".join([ele.strip() for ele in raw_doctring]).strip()

# # from redbaron import RedBaron
# # from typing import List, Tuple

# # from automata.core.code_indexing.python_code_inspector import PythonCodeInspector
# # from automata.core.search.symbol_graph import SymbolGraph
# # from automata.core.search.symbol_utils import convert_to_fst_object, get_rankable_symbols
# # from automata.core.search.symbol_types import Descriptor, Symbol

# # class CodePrinter:
# #     def __init__(
# #         self,
# #         graph: SymbolGraph,
# #         spacer: str = "  ",
# #         verbosity: int = 1,
# #         max_overview_depth: int = 1,
# #         max_dependency_depth: int = 0,
# #     ):
# #         self.graph = graph
# #         self.spacer = spacer
# #         self.verbosity = verbosity
# #         self.max_overview_depth = max_overview_depth
# #         self.max_detailed_depth = max_dependency_depth

# #         self.reset()

# #     def reset(self) -> None:
# #         self.message = ""
# #         self.obs_symbols = set([])
# #         self.global_level = 0

# #     def process_message(self, message: str, local_level: int):
# #         def indent(local_level: int) -> str:
# #             return self.spacer * (local_level + self.global_level)

# #         self.message += f"{indent(local_level)}{message}\n"

# #     def process_symbol(self, symbol: Symbol, local_depth=0) -> None:
# #         if local_depth > self.max_overview_depth:
# #             self.process_message(str(symbol.path), local_depth)
# #             return None
# #         if local_depth == 0:
# #             self.reset()
# #         # self.obs_symbols.add(symbol)
# #         try:
# #             ast_object = convert_to_fst_object(symbol)
# #         except Exception as e:
# #             print(f"Error {e} while converting symbol {symbol.descriptors[-1].name}.")
# #             return None

# #         self.process_headline(symbol, local_depth)
# #         self.process_methods(symbol, ast_object, local_depth)
# #         self.process_dependencies(symbol, local_depth)
# #         # self.process_nearest_symbols(symbol)

# #     def process_headline(self, symbol: Symbol, local_depth = 0) -> None:
# #         self.process_message(f"{symbol.path} --\n", local_depth)

# #     # TODO - It should not just be a binary cut when deciding how to abbreviate
# #     def process_methods(self, symbol: Symbol, ast_object: RedBaron, local_depth: int) -> None:
# #         methods = sorted(ast_object.find_all("DefNode"), key=lambda x: x.name)
# #         for method in methods:
# #             self.process_method(method, local_depth)
# #             # self.process_dependencies(symbol, local_depth)

# #     def process_method(self, method: RedBaron, local_depth: int) -> None:
# #         if CodePrinter._is_private_method(method):
# #             return
# #         for code_line in method.dumps().split("\n"):
# #             self.process_message(code_line, local_depth+1)


# #     def process_dependencies(self, symbol: Symbol, local_depth: int):
# #         self.process_message("Dependencies:", local_depth)
# #         all_dependencies = list(self.graph._get_symbol_dependencies(symbol))
# #         filtered_dependencies = get_rankable_symbols(all_dependencies)
# #         for dependency in filtered_dependencies:
# #             if not CodePrinter._is_class(dependency):
# #                 continue
# #             # Do not re-process self
# #             if dependency == symbol:
# #                 continue
# #             # self.obs_symbols.add(dependency)
# #             self.process_message(str(dependency.path), local_depth+2)


# #     def process_target_symbols(self, target_symbols: List[str], ranked_symbols_list: List[List[Tuple[Symbol, float]]]):
# #         for target_symbol, ranked_symbols in zip(target_symbols, ranked_symbols_list):
# #             for symbol, rank in ranked_symbols:
# #                 selected_symbol = False
# #                 for target_symbol in target_symbols:
# #                     if symbol.uri.endswith(target_symbol):
# #                         selected_symbol = True
# #                 if not selected_symbol:
# #                     continue
# #                 self.process_symbol(symbol)


# #     @staticmethod
# #     def _is_private_method(ast_object):
# #         return ast_object.name[0] == "_" and ast_object.name[1] != "_"

# #     @staticmethod
# #     def _is_class(symbol):
# #         return symbol.symbol_kind_by_suffix() == Descriptor.PythonKinds.Class

# #     @staticmethod
# #     def _get_docstring(ast_object):
# #         # Assuming PythonCodeInspector is accessible in the current scope
# #         raw_doctring = PythonCodeInspector._get_docstring(ast_object).split("\n")
# #         return "\n".join([ele.strip() for ele in raw_doctring]).strip()


# #     # def _format_code(self, source_code):
# #     #     return "\n".join([f"{self.indent(1)}{ele}" for ele in source_code.split("\n")])


# #         # if abbreviate:
# #         #     method_definition = f"{method.name}({method.arguments.dumps()})"
# #         #     return_annotation = (
# #         #         method.return_annotation.dumps() if method.return_annotation else "None"
# #         #     )
# #         #     self.message += f"{self.indent(1)}{method_definition} -> {return_annotation}\n"
# #         # else:
# #         # self.process_message(f"{self._format_code(method.dumps())}\n", local_depth+1)


# #     # def process_nearest_symbols(self, symbol, n_symbols=5):
# #     #     # TODO - add calculation for this object
# #     #     # ranked_results = ...
# #     #     self.message += f"\n{self.indent(1)}Nearest Symbols:\n"
# #     #     printed_nearby_symbols = 0
# #     #     for ranked_symbol, rank in ranked_results:
# #     #         if printed_nearby_symbols >= n_symbols:
# #     #             break
# #     #         if ranked_symbol.symbol_kind_by_suffix() != Descriptor.PythonKinds.Class:
# #     #             continue
# #     #         elif ranked_symbol in self.obs_symbols:
# #     #             continue
# #     #         else:
# #     #             printed_nearby_symbols += 1
# #     #             self.obs_symbols.add(symbol)
# #     #         self.message += f"{self.indent(2)}{ranked_symbol.path}\n"


# # # class CodeMetrics:
# # #     def __init__(self, ast_object):
# # #         self.ast_object = ast_object

# # #     @property
# # #     def lines_of_code_count(self) -> int:
# # #         return len(self.ast_object.dumps().split("\n"))

# # #     @property
# # #     def methods_count(self) -> int:
# # #         return len(self.ast_object.find_all("DefNode"))

# # #     @property
# # #     def fields_count(self) -> int:
# # #         # Assuming AssignNode represents a field
# # #         return len(self.ast_object.find_all("AssignNode"))

# # #     @property
# # #     def cyclomatic_complexity(self) -> str:
# # #         # Placeholder function, use actual computation for your use case
# # #         # For example, you can use the radon library for Python:
# # #         # from radon.complexity import cc_visit
# # #         # return cc_visit(ast_object.dumps())
# # #         return "Placeholder for cyclomatic complexity"

# # #     @property
# # #     def depth_of_inheritance(self) -> str:
# # #         # Placeholder function, use actual computation for your use case
# # #         return "Placeholder for depth of inheritance"


# # # from automata.core.code_indexing.python_ast_indexer import PythonASTIndexer
# # # from automata.core.search.symbol_factory import (
# # #     SymbolSearcherFactory,
# # #     SymbolGraphFactory,
# # #     SymbolRankFactory,
# # # )
# # # from automata.core.search.symbol_rank.symbol_rank import SymbolRank, SymbolRankConfig
# # # from automata.configs.config_enums import ConfigCategory
# # # from automata.core.utils import config_path, root_py_path
