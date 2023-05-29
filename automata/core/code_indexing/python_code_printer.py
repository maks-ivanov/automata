from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

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
        self.obs_symbols: Set[Symbol] = set([])
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
