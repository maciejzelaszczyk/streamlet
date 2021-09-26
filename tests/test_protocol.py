import asyncio

from src.comms import Message
from src.nodes import Node, HonestNode
from src.scheduling import Scheduler
from src.hashing import ad_hoc_hash
from tests.parser import args
from tests.utils import get_chains


# tests explicitly do not have to be DRY

def test_honest():
    scheduler = Scheduler(args)
    idxs = list(range(args.nodes))
    nodes = [HonestNode(idx=idx, idxs=idxs, args=args) for idx in idxs]

    asyncio.run(scheduler.run(nodes))

    chains = get_chains(nodes)
    
    assert len(chains) == 1  # safety
    assert len(chains[0]) == args.epochs - 1  # liveness


class DishonestOfflineNode(Node):
    def __init__(self, idx: int) -> None:
        self.idx = idx
        self.nodes = args.nodes
        self.delta = args.delta
        self.leader_count = 0

    async def at_time(self, t: int) -> None:
        epoch = t // (2*self.delta)
        leader = ad_hoc_hash(epoch, self.nodes)
        if leader == self.idx and (t / (2*self.delta)).is_integer():
            self.leader_count += 1
    
    async def on_message_received(self, msg: Message) -> None:
        pass


def test_offline():
    scheduler = Scheduler(args)
    honest_idxs = list(range(args.nodes - args.max_dishonest))
    dishonest_idxs = list(range(args.nodes - args.max_dishonest, args.nodes))
    idxs = honest_idxs + dishonest_idxs
    honest_nodes = [HonestNode(idx=idx, idxs=idxs, args=args) for idx in honest_idxs]
    dishonest_nodes = [DishonestOfflineNode(idx=idx) for idx in dishonest_idxs]
    nodes = honest_nodes + dishonest_nodes

    asyncio.run(scheduler.run(nodes))

    chains = get_chains(nodes[:len(honest_nodes)])

    dishonest_leaders_count = 0
    for dishonest_node in nodes[len(honest_nodes):]:
        dishonest_leaders_count += dishonest_node.leader_count
    
    # when dishonest nodes are present, there is a distinct possibility of not finalizing any chains
    assert len(chains) == 1 or len(chains) == 0  # safety
    
    # the number of final blocks for honest nodes depends on the hash function
    # for a non-deterministic ad hoc function, we cannot a priori decide on the number of final blocks
    # there is an upper bound on this number
    chain_len = len(chains[0]) if len(chains) > 0 else 0
    assert chain_len <= (args.epochs - 1) - dishonest_leaders_count  # liveness

test_offline()