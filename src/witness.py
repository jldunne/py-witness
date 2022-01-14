# importing the required modules
import argparse
import os
from dotenv import load_dotenv

from web3 import Web3

load_dotenv()
NODE_HTTP = os.getenv('NODE_HTTP')


def construct_access_list(transactions):
    block_addresses = {}
    transaction_access_list = {}

    # EIP-3584 block access list is structured as follows -
    #  block_access_list = [access_list_entry, ...]
    #
    # Each access_list_entry consists of the following:
    #  - address
    #  - storage keys associated with this address over whole block
    #  - list of 2-tuples (transaction index, list of storage keys for this tx)

    for tx in transactions:
        tx_index = tx.transactionIndex
        if not hasattr(tx, 'accessList'):
            continue
        for access_list in tx.accessList:
            address = access_list['address']
            if address not in block_addresses:
                block_addresses[address] = access_list['storageKeys']
            else:
                extra_slots = [i for i in block_addresses[address]+access_list['storageKeys']]
                for elem in extra_slots:
                    block_addresses[address].append(elem)
            if address not in transaction_access_list:
                transaction_access_list[address] = [(tx_index, sorted(access_list['storageKeys']))]
            else:
                transaction_access_list[address].append((tx_index, sorted(access_list['storageKeys'])))

    # at this point we have a dictionary of block addresses and storage slots
    # and another one of addresses -> (tx indices, per-transaction storage slots)
    # let's merge them together
    block_access_list = []
    for address in block_addresses.keys():
        access_list_entry = [address, sorted(block_addresses[address]), sorted(transaction_access_list[address], key=lambda x: x[0])]
        block_access_list.append(access_list_entry)

    # The block access list needs to be sorted according to the following rules:
    #   1. block access list is sorted by address
    #   2. storage_keys list is sorted
    #   3. transaction tuples are sorted by tx_index
    # 2 & 3 are taken care of in construction above

    # Sort the whole block_access_list by address
    block_access_list = sorted(block_access_list, key=lambda x: x[0])
    return block_access_list


def construct_partial_witness(transactions, w3, block_number):
    from_addresses = []
    to_addresses = []

    for tx in transactions:
        from_addresses.append(tx['from'])
        to_addresses.append(tx.to)

    addresses = set(from_addresses).union(set(to_addresses))
    addresses = list(addresses)

    proofs = []
    slots = []
    for i in range(0, 256):
        slots.append(i)

    for adx in addresses:
        print("Generating proof for account: "+adx)
        proof = w3.eth.get_proof(adx, slots, block_number)
        print("Appending proof")
        proofs.append(proof)

    return proofs


def print_block(args, w3):
    # get the block number
    block_number = args.block[0]
    block = w3.eth.get_block(block_number, full_transactions=True)

    if not block.transactions[0].accessList:
        return "This block does not contain tx-level access lists - aborting"
    block_access_list = construct_access_list(block.transactions)
    print(block)
    print("Now printing block access list...\n")
    print(block_access_list)

    print("Constructing partial witness")
    partial_witness = construct_partial_witness(block.transactions, w3, block_number)


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
