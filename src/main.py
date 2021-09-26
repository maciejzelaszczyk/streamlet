import asyncio

from src.nodes import HonestNode
from src.parser import args
from src.scheduling import Scheduler


def main():
    scheduler = Scheduler(args)
    idxs = list(range(args.nodes))
    nodes = [HonestNode(idx=idx, idxs=idxs, args=args) for idx in idxs]
    asyncio.run(scheduler.run(nodes))


if __name__ == "__main__":
    main()
