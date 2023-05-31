import argparse
import logging
import os
import textwrap
from typing import Any, Dict, Tuple

import jsonpickle
import openai

from automata.config import OPENAI_API_KEY
from automata.configs.config_enums import ConfigCategory
from automata.core.code_indexing.python_code_printer import CodePrinter
from automata.core.search.symbol_factory import (
    SymbolGraphFactory,
    SymbolRankFactory,
    SymbolSearcherFactory,
)
from automata.core.search.symbol_rank.symbol_rank import SymbolRank, SymbolRankConfig
from automata.core.search.symbol_types import Symbol
from automata.core.search.symbol_utils import convert_to_fst_object
from automata.core.utils import config_path

logger = logging.getLogger(__name__)


def get_filtered_ranked_symbols(kwargs: Dict[str, Any], ranker: SymbolRank):
    selected_symbols = []
    for symbol, _rank in ranker.get_ranks():
        if kwargs.get("selection_filter", "") in symbol.uri:
            selected_symbols.append(symbol)
            if len(set(selected_symbols)) >= kwargs.get("top_n_symbols", 0):
                break
    return selected_symbols


def get_completion(selected_symbol: Symbol, symbol_overview: str):
    example = textwrap.dedent(
        """
        8.3. Handling Exceptions
        It is possible to write programs that handle selected exceptions. Look at the following example, which asks the user for input until a valid integer has been entered, but allows the user to interrupt the program (using Control-C or whatever the operating system supports); note that a user-generated interruption is signalled by raising the KeyboardInterrupt exception.

        >>>
        while True:
            try:
                x = int(input("Please enter a number: "))
                break
            except ValueError:
                print("Oops!  That was no valid number.  Try again...")

        The try statement works as follows.
        """
    )

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Generate the documentation for {selected_symbol.path} using the context shown below -\n {symbol_overview}."
                f" The outputed documentation should include an overview section, related symbols, examples, limitations."
                f" Examples should be comprehensive, like in the original Python Library documentation, like so - {example}."
                f" Do not include the local file hiearchy, that is just for contextual reference.",
            }
        ],
    )
    if not completion.choices:
        return "Error: No completion found"
    return completion.choices[0]["message"]["content"]


def load_docs(kwargs: Dict[str, Any]) -> Dict[Symbol, Tuple[str, str, str]]:
    doc_path = os.path.join(
        config_path(),
        ConfigCategory.SYMBOLS.value,
        kwargs.get("documentation_path", "symbol_documentation.json"),
    )

    docs: Dict[Symbol, Tuple[str, str, str]] = {}
    if kwargs.get("update_docs"):
        try:
            if not os.path.exists(doc_path):
                raise Exception("No docs to update.")
            with open(doc_path, "r") as file:
                docs = jsonpickle.decode(file.read())
        except Exception as e:
            logger.error(f"Failed to load docs: {e}")
    return docs


def save_docs(kwargs: Dict[str, Any], docs: Dict[Symbol, Tuple[str, str, str]]):
    doc_path = os.path.join(
        config_path(),
        ConfigCategory.SYMBOLS.value,
        kwargs.get("documentation_path", "symbol_documentation.json"),
    )

    pickle_str = jsonpickle.encode(docs)

    with open(doc_path, "w") as file:
        file.write(pickle_str)


def main(*args, **kwargs):
    graph = SymbolGraphFactory().create()
    config = SymbolRankConfig()
    subgraph = graph.get_rankable_symbol_subgraph(
        flow_rank=kwargs.get("rank_direction", "bidirectional")
    )
    ranker = SymbolRankFactory().create(subgraph, config)
    symbol_searcher = SymbolSearcherFactory().create()

    docs = load_docs(kwargs)
    selected_symbols = get_filtered_ranked_symbols(kwargs, ranker)
    for selected_symbol in selected_symbols:
        raw_code = convert_to_fst_object(selected_symbol).dumps()
        if (
            selected_symbol in docs
            and docs[selected_symbol][0] == raw_code
            and not kwargs.get("hard_refresh")
        ):
            print(f"Continuing on {selected_symbol}")
            continue
        print(f"Generating docs for {selected_symbol}")
        abbreviated_selected_symbol = selected_symbol.uri.split("/")[1].split("#")[0]
        search_results = symbol_searcher.symbol_rank_search(abbreviated_selected_symbol)
        search_list = [result[0] for result in search_results]

        printer = CodePrinter(graph)
        printer.process_symbol(selected_symbol, search_list)
        symbol_overview = printer.message
        completion = get_completion(selected_symbol, symbol_overview)
        docs[selected_symbol] = (raw_code, symbol_overview, completion)
        break

    save_docs(kwargs, docs)


if __name__ == "__main__":
    openai.api_key = OPENAI_API_KEY

    # Function for argument parsing
    def parse_args():
        parser = argparse.ArgumentParser(
            description="Update documentation based on local code changes."
        )
        parser.add_argument("-i", "--input", help="The path to the file that needs documentation.")
        parser.add_argument(
            "-s", "--selection_filter", default="Automata", help="Selection criteria for symbols."
        )
        parser.add_argument(
            "-n", "--top_n_symbols", type=int, default=20, help="Number of top symbols to select."
        )
        parser.add_argument(
            "-u", "--update_docs", action="store_true", help="Flag to update the docs."
        )
        parser.add_argument(
            "-r",
            "--hard_refresh",
            action="store_true",
            help="Should we re-run files with no code-diff?",
        )
        parser.add_argument(
            "-documentation_path",
            default="symbol_documentation.json",
            help="Selection criteria for symbols.",
        )
        parser.add_argument(
            "-rank_direction", default="bidirectional", help="Selection criteria for symbols."
        )
        return parser.parse_args()

    # Parse the arguments
    args = parse_args()

    # Call the main function with parsed arguments
    result = main(**vars(args))
    print("Result = ", result)
