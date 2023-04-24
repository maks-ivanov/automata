import ast
import json
import os
from _ast import Assign, Module, Name
from collections import namedtuple
from copy import copy

import networkx as nx

Node = namedtuple(
    "Node",
    [
        "name",
        "type",
        "lineno",
        "end_lineno",
        "col_offset",
        "end_col_offset",
        "source_file",
        "parent_entity",
    ],
)


class CodebaseGraphBuilder(ast.NodeVisitor):
    def __init__(self, graph, file_path, parent_entity=None):
        self.graph = graph
        self.file_path = file_path
        self.parent_entity = parent_entity

    def visit_Module(self, node: Module):
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Import(self, node):
        for alias in node.names:
            import_node = Node(
                name=alias.name,
                type="import",
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                col_offset=node.col_offset,
                end_col_offset=node.end_col_offset,
                source_file=self.file_path,
                parent_entity=self.parent_entity,
            )
            # generate a uid
            id = f"{import_node.source_file}-{import_node.name}-{import_node.type}-{import_node.lineno}"
            self.graph.add_node(id, **import_node._asdict())
            self.graph.add_edge(self.file_path, id, type="imports")

    def visit_ImportFrom(self, node):
        for alias in node.names:
            import_node = Node(
                name=alias.name,
                type="import",
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                col_offset=node.col_offset,
                end_col_offset=node.end_col_offset,
                source_file=self.file_path,
                parent_entity=node.module,
            )

            id = f"{import_node.source_file}-{import_node.name}-{import_node.type}-{import_node.lineno}"
            self.graph.add_node(id, **import_node._asdict())
            self.graph.add_edge(self.file_path, id, type="imports")

    def visit_FunctionDef(self, node: ast.FunctionDef):
        func_node = Node(
            name=node.name,
            type="function_define",
            lineno=node.lineno,
            end_lineno=node.end_lineno,
            col_offset=node.col_offset,
            end_col_offset=node.end_col_offset,
            source_file=self.file_path,
            parent_entity=self.parent_entity,
        )

        id = f"{func_node.source_file}-{func_node.name}-{func_node.type}-{func_node.lineno}"
        self.graph.add_node(id, **func_node._asdict())
        self.graph.add_edge(self.file_path, id, type="contains")

        if self.parent_entity:
            self.graph.add_edge(self.parent_entity, id, type="contains")

        self.parent_entity = id
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Call(self, node):
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        call_node = Node(
            name=func_name,
            type="function_call",
            lineno=node.lineno,
            end_lineno=node.end_lineno,
            col_offset=node.col_offset,
            end_col_offset=node.end_col_offset,
            source_file=self.file_path,
            parent_entity=self.parent_entity,
        )

        id = f"{call_node.source_file}-{call_node.name}-{call_node.type}-{call_node.lineno}"
        self.graph.add_node(id, **call_node._asdict())
        self.graph.add_edge(self.file_path, id, type="contains")

        if self.parent_entity:
            self.graph.add_edge(self.parent_entity, id, type="contains")

    def visit_ClassDef(self, node):
        class_node = Node(
            name=node.name,
            type="class",
            lineno=node.lineno,
            end_lineno=node.end_lineno,
            col_offset=node.col_offset,
            end_col_offset=node.end_col_offset,
            source_file=self.file_path,
            parent_entity=self.parent_entity,
        )

        id = f"{class_node.source_file}-{class_node.name}-{class_node.type}-{class_node.lineno}"
        self.graph.add_node(id, **class_node._asdict())
        self.graph.add_edge(self.file_path, id, type="contains")

        if self.parent_entity:
            self.graph.add_edge(self.parent_entity, id, type="contains")

        self.parent_entity = id
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Assign(self, node: Assign):
        for target in node.targets:
            if isinstance(target, Name):
                var_node = Node(
                    name=target.id,
                    type="variable",
                    lineno=node.lineno,
                    end_lineno=node.end_lineno,
                    col_offset=node.col_offset,
                    end_col_offset=node.end_col_offset,
                    source_file=self.file_path,
                    parent_entity=self.parent_entity,
                )
                id = f"{var_node.source_file}-{var_node.name}-{var_node.type}-{var_node.lineno}"
                self.graph.add_node(id, **var_node._asdict())
                if self.parent_entity:
                    self.graph.add_edge(self.parent_entity, id, type="contains")
                self.graph.add_edge(self.file_path, id, type="contains")


def process_file(graph, file_path: str):
    with open(file_path, "r") as f:
        try:
            file_contents = f.read()
            tree = ast.parse(file_contents)
            CodebaseGraphBuilder(graph, file_path).visit(tree)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")


def build_codebase_graph(codebase_path: str) -> nx.DiGraph:
    graph = nx.DiGraph()
    for root, dirs, files in os.walk(codebase_path):
        if _is_excluded(root):
            continue
        if root not in graph.nodes:
            graph.add_node(root, **{"name": root, "type": "directory"})
        for dir in dirs:
            if _is_excluded(dir):
                continue
            dir_path = os.path.join(root, dir)
            graph.add_node(dir_path, **{"name": dir_path, "type": "directory"})
            graph.add_edge(root, dir_path, type="contains")

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                graph.add_node(file_path, **{"name": file_path, "type": "file"})
                graph.add_edge(root, file_path, type="contains")
                process_file(graph, file_path)
    return graph


def get_entity(graph: nx.DiGraph, name: str) -> dict:
    if name in graph.nodes:
        node = graph.nodes[name]
        if "name" not in node:
            node["name"] = name
        return node
    else:
        return {"Entity not found": None}


def get_entity_with_children(graph: nx.DiGraph, name: str) -> dict:
    if name in graph.nodes:
        node = copy(graph.nodes[name])
        if "name" not in node:
            node["name"] = name
        children = sorted(
            [get_entity(graph, child) for child in graph.successors(name)],
            key=lambda x: x["lineno"] if "lineno" in x else x["name"],
        )
        node["children"] = children
        return node
    else:
        return {"Entity not found": None}


def get_entity_with_children_format(graph: nx.DiGraph, name: str) -> str:
    return str(json.dumps(get_entity_with_children(graph, name), indent=2))


def get_entities_by_type(graph: nx.DiGraph, type: str) -> list:
    return [
        get_entity(graph, node)
        for node in graph.nodes
        if "type" in graph.nodes[node] and graph.nodes[node]["type"] == type
    ]


def get_entities_with_children_by_type(graph: nx.DiGraph, type: str) -> list:
    return [
        get_entity_with_children(graph, node)
        for node in graph.nodes
        if "type" in graph.nodes[node] and graph.nodes[node]["type"] == type
    ]


def get_entities_by_type_format(graph: nx.DiGraph, type: str) -> str:
    return str(json.dumps(get_entities_by_type(graph, type), indent=2))


def get_entities_with_children_by_type_format(graph: nx.DiGraph, type: str) -> str:
    return str(json.dumps(get_entities_with_children_by_type(graph, type), indent=2))


def get_codebase_tree(graph: nx.DiGraph) -> dict:
    root = [node for node in graph.nodes if graph.in_degree(node) == 0][0]
    tree = visit_directory_tree_node(graph, root)
    return tree


def visit_directory_tree_node(graph, node_name):
    node_dict = copy(get_entity(graph, node_name))
    if not graph.successors(node_name):
        return node_dict
    node_dict["children"] = [
        visit_directory_tree_node(graph, child)
        for child in graph.successors(node_name)
        if graph.nodes[child]["type"] == "directory" or graph.nodes[child]["type"] == "file"
    ]
    return node_dict


def get_codebase_tree_format(graph: nx.DiGraph) -> str:
    return str(json.dumps(get_codebase_tree(graph), indent=2))


def _is_excluded(path):
    exclusions = [
        ".git",
        ".gitignore",
        ".gitattributes",
        ".gitmodules",
        "__pycache__",
        ".idea",
        "build",
        "local_env",
        "dist",
        "chroma",
        "egg",  # exclude a few common directories in the
        ".git",  # root of the project
        ".hg",
        ".mypy_cache",
        ".tox",
        ".venv",
        "_build",
        "buck-out",
        "random",
        "sqlite",
        ".pytest",
    ]
    for exclusion in exclusions:
        if exclusion in path:
            return True
    return False


# Example usage:
if __name__ == "__main__":
    codebase_path = "/Users/ivanovm/proj/improved-spork/spork/"
    graph = build_codebase_graph(codebase_path)
