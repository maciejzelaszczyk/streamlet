import argparse

# tests explicitly do not have to be DRY

parser = argparse.ArgumentParser(description="Config values for Streamlet protocol")
parser.add_argument("-d", "--delta", default=1, type=int, help="Time delta")
parser.add_argument("-n", "--nodes", default=10, type=int, help="Number of nodes")
parser.add_argument(
    "-m_dis",
    "--max_dishonest",
    default=3,
    type=int,
    help="Assumed maximum number of dishonest nodes",
)
parser.add_argument("-tz", "--t_zero", default=0, type=int, help="Protocol start time")
parser.add_argument(
    "-e", "--epochs", default=100, type=int, help="Number of epochs to run"
)

args = parser.parse_args()
