from dataclasses import dataclass
from typing import Optional, Union


@dataclass(frozen=True)
class Block:
    block_id: str
    epoch: int
    parent: Optional[str]
    content: Optional[str]


@dataclass(frozen=True)
class Vote:
    sender_idx: int
    block_id: str


@dataclass(frozen=True)
class Message:
    received_from: int
    send_to: int
    content: Union[Block, Vote]
