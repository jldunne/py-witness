# importing the required modules
import argparse
import os
from dotenv import load_dotenv

from web3 import Web3

load_dotenv()
NODE_HTTP = os.getenv('NODE_HTTP')


def print_block(args, w3):
    # get the block number
    block_number = args.block[0]
    block = w3.eth.get_block(block_number)
    print(block)


def main():
    # init connection from env
    node_url = NODE_HTTP
    w3 = Web3(Web3.HTTPProvider(node_url))
    if not w3.isConnected():
        print('Connection to node failed! Please check your env')

    parser = argparse.ArgumentParser(
        description="A command line tool to generate access lists and witnesses from blocks")

    parser.add_argument("-b", "--block", type=int, nargs=1,
                        metavar="block-number", default=None,
                        help="Returns the specified block")

    args = parser.parse_args()

    if args.block is not None:
        print_block(args, w3)


if __name__ == "__main__":
    # calling the main function
    main()
