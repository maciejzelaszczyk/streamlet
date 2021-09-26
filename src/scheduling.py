import argparse
import asyncio
from collections import deque
import logging

from src.nodes import Node


logging.basicConfig(level=logging.INFO)


class Scheduler:
    def __init__(self, args: argparse.Namespace) -> None:
        self.t = args.t_zero
        self.epochs = args.epochs
        self.delta = args.delta
        self.q = deque()
    async def run(self, nodes: list[Node]) -> None:
        while True:
            epoch = self.t // 2
            for future in asyncio.as_completed([node.at_time(self.t) for node in nodes]):
                messages = await future
                if messages is not None:
                    self.q.extend(messages)
            while True:
                try:
                    msg = self.q.popleft()
                    logging.info(f"epoch={epoch} | {msg}")
                except IndexError:
                    logging.info(f"epoch={epoch} | Queue exhausted.")
                    break
                else:
                    for future in asyncio.as_completed([node.on_message_received(msg) for node in nodes if node.idx == msg.send_to]):
                        messages = await future
                        if messages is not None:
                            self.q.extend(messages)
            if epoch == self.epochs:
                break
            self.t += 2*self.delta