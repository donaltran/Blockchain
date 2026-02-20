import time
import json
from typing import List, Dict, Any
from src.block import Block, Transaction
import logging

logger = logging.getLogger(__name__)


class Blockchain:

    def __init__(self, difficulty: int = 2, mining_reward: float = 10.0):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.mining_reward = mining_reward
        self.pending_transactions: List[Transaction] = []
        self.create_genesis_block()

    def create_genesis_block(self) -> Block:
        genesis_transaction = Transaction(
            sender="GENESIS",
            recipient="GENESIS",
            amount=0,
            timestamp=time.time()
        )

        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[genesis_transaction],
            previous_hash="0",
            difficulty=self.difficulty
        )

        self.chain.append(genesis_block)
        logger.info("Genesis block created")
        return genesis_block

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> bool:
        # Validate transaction
        if not self.is_valid_transaction(transaction):
            logger.warning(f"Invalid transaction rejected: {transaction}")
            return False

        # Check if sender has sufficient balance (excluding mining rewards)
        if transaction.sender != "MINING_REWARD":
            sender_balance = self.get_balance(transaction.sender)
            if sender_balance < transaction.amount:
                logger.warning(f"Insufficient balance for transaction: {transaction}")
                return False

        self.pending_transactions.append(transaction)
        logger.info(f"Transaction added to pool: {transaction}")
        return True

    def is_valid_transaction(self, transaction: Transaction) -> bool:
        # Genesis and mining reward transactions are always valid
        if transaction.sender in ["GENESIS", "MINING_REWARD"]:
            return True

        # Check for valid amount
        if transaction.amount <= 0:
            return False

        # Check for valid addresses
        if not transaction.sender or not transaction.recipient:
            return False

        # Cannot send to self
        if transaction.sender == transaction.recipient:
            return False

        # TODO: Add signature verification when wallet integration complete

        return True

    def mine_pending_transactions(self, mining_reward_address: str) -> Block:
        # Add mining reward transaction
        reward_transaction = Transaction(
            sender="MINING_REWARD",
            recipient=mining_reward_address,
            amount=self.mining_reward,
            timestamp=time.time()
        )

        transactions = [reward_transaction] + self.pending_transactions

        # Create new block
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=transactions,
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty
        )

        # Mine the block
        logger.info(f"Mining block #{new_block.index}...")
        start_time = time.time()
        new_block.mine_block(self.difficulty)
        mining_time = time.time() - start_time

        logger.info(f"Block #{new_block.index} mined in {mining_time:.2f}s with hash: {new_block.hash}")

        # Add to chain
        self.chain.append(new_block)

        # Clear pending transactions
        self.pending_transactions = []

        return new_block

    def get_balance(self, address: str) -> float:
        balance = 0.0

        for block in self.chain:
            for transaction in block.transactions:
                if transaction.recipient == address:
                    balance += transaction.amount
                if transaction.sender == address:
                    balance -= transaction.amount

        # Include pending transactions
        for transaction in self.pending_transactions:
            if transaction.sender == address:
                balance -= transaction.amount

        return balance

    def is_chain_valid(self) -> bool:
        # Check genesis block
        if len(self.chain) == 0:
            return False

        # Validate each block
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Validate current block
            if not current_block.is_valid(previous_block):
                logger.error(f"Block #{current_block.index} is invalid")
                return False

        logger.info("Blockchain validation successful")
        return True

    def replace_chain(self, new_chain: List[Block]) -> bool:
        if len(new_chain) <= len(self.chain):
            logger.info("New chain is not longer than current chain")
            return False

        # Validate new chain
        temp_blockchain = Blockchain(difficulty=self.difficulty)
        temp_blockchain.chain = new_chain

        if not temp_blockchain.is_chain_valid():
            logger.warning("New chain is invalid")
            return False

        # Replace chain
        self.chain = new_chain
        logger.info("Chain replaced with longer valid chain")
        return True

    def get_transaction_history(self, address: str) -> List[Transaction]:
        transactions = []

        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address or transaction.recipient == address:
                    transactions.append(transaction)

        return transactions

    def to_dict(self) -> Dict[str, Any]:
        return {
            'chain': [block.to_dict() for block in self.chain],
            'difficulty': self.difficulty,
            'mining_reward': self.mining_reward,
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'chain_length': len(self.chain)
        }

    def save_to_file(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Blockchain saved to {filename}")

    @classmethod
    def load_from_file(cls, filename: str) -> 'Blockchain':
        with open(filename, 'r') as f:
            data = json.load(f)

        blockchain = cls(
            difficulty=data['difficulty'],
            mining_reward=data['mining_reward']
        )

        # Load chain (skip genesis block as it's already created)
        blockchain.chain = [Block.from_dict(block_data) for block_data in data['chain']]

        # Load pending transactions
        blockchain.pending_transactions = [
            Transaction(**tx_data) for tx_data in data['pending_transactions']
        ]

        logger.info(f"Blockchain loaded from {filename}")
        return blockchain

    def get_statistics(self) -> Dict[str, Any]:
        total_transactions = sum(len(block.transactions) for block in self.chain)

        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'pending_transactions': len(self.pending_transactions),
            'difficulty': self.difficulty,
            'mining_reward': self.mining_reward,
            'latest_block_hash': self.get_latest_block().hash,
            'is_valid': self.is_chain_valid()
        }

    def __repr__(self) -> str:
        return f"Blockchain(blocks={len(self.chain)}, difficulty={self.difficulty})"

