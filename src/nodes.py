import argparse
import copy
import uuid
from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Optional, Union

import networkx as nx
from networkx.algorithms.dag import dag_longest_path

from src.comms import Block, Message, Vote
from src.hashing import ad_hoc_hash


class Node(ABC):
    @abstractmethod
    def __init__(self, idx: int) -> None:
        self.idx = idx

    @abstractmethod
    async def at_time(self, t: int) -> Optional[list[Message]]:
        """Method to be called at specific time step."""

    @abstractmethod
    async def on_message_received(self, msg: Message) -> Optional[list[Message]]:
        """Method to be called on receit of a message."""


class HonestNode(Node):
    def __init__(self, idx: int, idxs: list[int], args: argparse.Namespace) -> None:
        self.nodes = args.nodes
        self.max_dishonest = args.max_dishonest
        self.delta = args.delta
        self.final: list[Block] = []
        self.notarized = nx.DiGraph()
        self.idx = idx
        self.idxs = idxs
        self.block: Optional[Block] = None
        self.nodes_voted: list[int] = []
        self.votes_for_block = 0

    def _longest_notarized(self) -> list[Block]:
        return dag_longest_path(self.notarized)

    def _head_longest_notarized(self) -> Optional[str]:
        longest_notarized = self._longest_notarized()
        head = longest_notarized[-1].block_id if len(longest_notarized) > 0 else None
        return head

    def _create_block(self, epoch) -> Block:
        block_id = str(uuid.uuid4())
        if epoch == 0:
            block = Block(block_id=block_id, epoch=0, parent=None, content=None)
        else:
            head = self._head_longest_notarized()
            content = f"Some placeholder content for epoch {epoch}."
            block = Block(block_id=block_id, epoch=epoch, parent=head, content=content)
        return block

    async def at_time(self, t: int) -> Optional[list[Message]]:
        epoch = t // (2 * self.delta)
        leader = ad_hoc_hash(epoch, self.nodes)
        if leader == self.idx and (t / (2 * self.delta)).is_integer():
            self.block = self._create_block(epoch)
            messages = [
                Message(received_from=self.idx, send_to=idx, content=self.block)
                for idx in self.idxs
            ]
            return messages
        return None

    @singledispatchmethod
    def _handle_content(self, content: Union[Block, Vote]) -> Optional[list[Message]]:
        raise NotImplementedError

    @_handle_content.register
    def _(self, content: Block) -> Optional[list[Message]]:
        self.block = content
        self.votes_for_block = 0
        head = self._head_longest_notarized()
        if self.block.parent == head:
            vote = Vote(sender_idx=self.idx, block_id=self.block.block_id)
            messages = [
                Message(received_from=self.idx, send_to=idx, content=vote)
                for idx in self.idxs
            ]
            return messages
        return None

    def _notarize_block(self, block_to_notarize: Block) -> None:
        self.notarized.add_node(block_to_notarize)
        for block_notarized in self.notarized:
            if (
                block_notarized.block_id == block_to_notarize.parent
                and len(self.notarized.nodes) > 1
            ):
                self.notarized.add_edge(block_notarized, block_to_notarize)
                break

    def _chains(self) -> list[list[Block]]:
        root = None
        leaves: list[Block] = []
        for block_notarized in self.notarized:
            if self.notarized.in_degree(block_notarized) == 0:
                root = block_notarized
            if self.notarized.out_degree(block_notarized) == 0:
                leaves = leaves + [block_notarized]
        chains = [
            chain
            for leaf in leaves
            for chain in nx.all_simple_paths(self.notarized, root, leaf)
        ]
        return chains

    def _finalize_blocks(self, chains) -> None:
        for chain in chains:
            chain_reversed = list(reversed(list(enumerate(chain))))
            chain_reversed_chunked = [
                chain_reversed[i : i + 3] for i in range(0, len(chain_reversed), 3)
            ]
            for chunk in chain_reversed_chunked:
                if (
                    len(chunk) == 3
                    and chunk[0][1].epoch == chunk[1][1].epoch + 1
                    and chunk[1][1].epoch == chunk[2][1].epoch + 1
                ):
                    idx_final = chunk[2][0]
                    chain_to_finalize = chain[: idx_final + 1]
                    final = list(set(self.final + chain_to_finalize))
                    self.final = sorted(final, key=lambda x: x.epoch)

    @_handle_content.register  # type: ignore
    def _(self, content: Vote) -> None:
        if content.sender_idx in self.nodes_voted:
            return None
        self.nodes_voted = self.nodes_voted + [content.sender_idx]
        if content.block_id == self.block.block_id:  # type: ignore
            self.votes_for_block += 1
            if self.votes_for_block == 2 * self.max_dishonest + 1:
                block_to_notarize = copy.deepcopy(
                    self.block
                )  # current block can be mutated in the future
                # mutation of notarized blocks
                self._notarize_block(block_to_notarize)  # type: ignore
                chains = self._chains()
                self._finalize_blocks(chains)

    async def on_message_received(self, msg: Message) -> Optional[list[Message]]:
        messages = self._handle_content(msg.content)
        return messages
