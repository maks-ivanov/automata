from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import networkx as nx
import numpy as np
from redbaron import RedBaron

from automata.core.search.symbol_types import Descriptor, Symbol, SymbolEmbedding
from automata.tools.python_tools.python_indexer import PythonIndexer


def convert_to_fst_object(symbol: Symbol, indexer: Optional[PythonIndexer] = None) -> RedBaron:
    """
    Returns the RedBaron object for the given symbol.
    Args:
        symbol (str): The symbol which corresponds to a module, class, or method.
        indexer: The PythonIndexer to use to find the symbol.
    Returns:
        Union[ClassNode, DefNode]: The RedBaron FST object for the class or method, or None if not found.
    """

    # Extract the module path, class/method name from the symbol
    descriptors = list(symbol.descriptors)
    obj = None
    indexer = indexer or PythonIndexer.default()  # this is to make default lazy.
    # The optional argument is to allow us to run this function in mulitprocessing in the future,
    # because indexer is not picklable (because redbaron objects are not picklable)
    # So the indexer would have to be created and destroyed in each process.

    while descriptors:
        top_descriptor = descriptors.pop(0)
        if (
            Descriptor.convert_scip_to_python_suffix(top_descriptor.suffix)
            == Descriptor.PythonKinds.Module
        ):
            module_name = top_descriptor.name
            if module_name.startswith("automata."):
                module_name = module_name[len("automata.") :]  # indexer omits this
            obj = indexer.module_dict.get(module_name)
            # TODO - Understand why some modules might be None
            if not obj or "test" in top_descriptor.name:
                raise ValueError(f"Module descriptor {top_descriptor.name} not found")
        elif (
            Descriptor.convert_scip_to_python_suffix(top_descriptor.suffix)
            == Descriptor.PythonKinds.Class
        ):
            if not obj:
                raise ValueError("Class descriptor found without module descriptor")
            obj = obj.find("class", name=top_descriptor.name)
        elif (
            Descriptor.convert_scip_to_python_suffix(top_descriptor.suffix)
            == Descriptor.PythonKinds.Method
        ):
            if not obj:
                raise ValueError("Method descriptor found without module or class descriptor")
            obj = obj.find("def", name=top_descriptor.name)
    if not obj:
        raise ValueError(f"Symbol {symbol} not found")
    return obj


def get_rankable_symbols(
    symbols: List[Symbol],
    filter_strings=("setup", "stdlib"),  # TODO - Revisit what strings we should filter on.
    accepted_kinds=(Descriptor.PythonKinds.Method, Descriptor.PythonKinds.Class),
) -> List[Symbol]:
    """
    Filter out symbols that are not relevant for the embedding map.

    Args:
        symbols: List of symbols to filter
    Returns:
        List of filtered symbols
    """
    filtered_symbols = []

    for symbol in symbols:
        do_continue = False
        for filter_string in filter_strings:
            if filter_string in symbol.uri:
                do_continue = True
                break
        if do_continue:
            continue

        symbol_kind = symbol.symbol_kind_by_suffix()
        if symbol_kind not in accepted_kinds:
            continue
        if (
            Symbol.is_protobuf(symbol)
            or Symbol.is_local(symbol)
            or Symbol.is_meta(symbol)
            or Symbol.is_parameter(symbol)
        ):
            continue

        filtered_symbols.append(symbol)

    return filtered_symbols


def find_and_replace_in_modules(old_name: str, new_name: str, do_write: bool = True) -> int:
    """
    Renames a function or class in all modules.
    Args:
        old_name (str): The old name of the function or class.
        new_name (str): The new name of the function or class.
    """
    # counts = 0
    # for module in converter._module_dict.values():
    #     # Find all function or class nodes with the old name
    #     func_or_class_nodes = module.find_all(("def", "class"), name=old_name)
    #     counts += str(func_or_class_nodes).count(old_name)
    #     for node in func_or_class_nodes:
    #         # Rename the node
    #         node.name = new_name
    #     # Find all NameNode's (these could be function calls or variable names)
    #     name_nodes = module.find_all("name", value=old_name)
    #     for node in name_nodes:
    #         # Rename the node
    #         node.value = new_name
    # if do_write:
    #     converter._write_modules()
    # return counts
    raise NotImplementedError("Should probably use a library for this")


def find_pattern_in_modules(pattern: str) -> Dict[str, List[int]]:
    """
    Finds exact line matches for a given pattern string in all modules.
    Args:
        pattern (str): The pattern string to search for.
    Returns:
        Dict[str, List[int]]: A dictionary with module paths as keys and a list of line numbers as values.
    """
    matches = {}
    indexer = PythonIndexer.default()
    for module_path, module in indexer.module_dict.items():
        lines = str(module).splitlines()
        line_numbers = [i + 1 for i, line in enumerate(lines) if pattern in line.strip()]
        if line_numbers:
            matches[module_path] = line_numbers
    return matches


def sync_graph_and_dict(
    graph: nx.DiGraph, dictionary: Dict[Symbol, SymbolEmbedding]
) -> Tuple[nx.DiGraph, Dict[Symbol, SymbolEmbedding]]:
    """
    Function to synchronize a graph and a dictionary.
    It removes nodes in the graph that are not in the dictionary, and
    keys in the dictionary that are not in the graph.

    :param graph: A networkx DiGraph object.
    :param dictionary: A dictionary to synchronize with the graph.
    :return: A tuple containing two elements: the synchronized graph and dictionary.
    """

    # Use list() to create a copy of the node list, as you can't modify a list while iterating over it
    for node in list(graph.nodes()):
        if node not in dictionary:
            graph.remove_node(node)

    # Again, use list() to create a copy of the key list
    for key in list(dictionary.keys()):
        if key not in graph:
            del dictionary[key]

    return graph, dictionary


def shifted_z_score_sq(values: Union[List[float], np.ndarray]):
    """
    Compute z-score of a list of values.
    Args:
        values: List of values to compute z-score for.
    Returns:
        List of z-scores.
    """
    if not isinstance(values, np.ndarray):
        values = np.array(values)

    mean = np.mean(values)
    std_dev = np.std(values)
    zscores = [(value - mean) / std_dev for value in values]
    return (zscores - np.min(zscores)) ** 2


def transform_dict_values(
    dictionary: Dict[Any, float], func: Callable[[List[float]], List[float]]
):
    """
    Apply a function to each value in a dictionary and return a new dictionary.
    Args:
        dictionary: Dictionary to transform.
        func: Function to apply to each value.
    Returns:
        Dictionary with transformed values.
    """
    # Apply the function to the accumulated values
    transformed_values = func([dictionary[key] for key in dictionary])

    # Re-distribute the transformed values back into the dictionary
    transformed_dict = {}
    for i, key in enumerate(dictionary):
        transformed_dict[key] = transformed_values[i]
    return transformed_dict