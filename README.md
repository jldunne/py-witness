## py-witness

A WIP command line tool that verifies interplay between Ethereum EIP-3584 block access lists and state stree witnesses.

### Requirements

Set up a virtual environment, and install required dependencies. In the root directory, run

```
pip install virtualenv
virtualenv -p python3 venv
. venv/bin/activate
```

The project uses `web3.py` to connect to a node in order to retrieve block and state information. In order to run it,
create a `.env` file in the root directory.

```
NODE_HTTP = '<address of the node to connect to>'
```

### Usage

```
# Retrieve block information given a block number
python3 witness.py --block 13199406
```
