import networkx as nx

from src.comms import Block
from src.nodes import Node


def blocks_finalized_union(nodes: list[Node]) -> list[Block]:
    blocks_finalized: list[Block] = []
    for node in nodes:
        blocks_finalized = blocks_finalized + node.final
    blocks_finalized_union = sorted(list(set(blocks_finalized)), key=lambda x: x.epoch)
    return blocks_finalized_union


def finalized_graph(blocks_finalized_union: list[Block]) -> nx.DiGraph:
    final = nx.DiGraph()
    final.add_nodes_from(blocks_finalized_union)
    for block_finalized in final:
        for block in final:
            if block_finalized.block_id == block.parent and len(final.nodes) > 1:
                final.add_edge(block_finalized, block)
    return final


def chains_from_graph(final: nx.DiGraph) -> list[list[Block]]:
    roots: list[Block] = []
    leaves: list[Block] = []
    for block_finalized in final:
        if final.in_degree(block_finalized) == 0:
            roots = roots + [block_finalized]
        if final.out_degree(block_finalized) == 0:
            leaves = leaves + [block_finalized]
    chains = [
        chain
        for root in roots
        for leaf in leaves
        for chain in nx.all_simple_paths(final, root, leaf)
    ]
    return chains


def get_chains(nodes: list[Node]) -> list[list[Block]]:
    blocks_finalized = blocks_finalized_union(nodes)
    final = finalized_graph(blocks_finalized)
    chains = chains_from_graph(final)
    return chains
