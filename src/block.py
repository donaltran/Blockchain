import hashlib
import hashlib as hasher
import time
import json
from typing import List, Dict, Any

class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float, timestamp: float = None,
                 signature: str = None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or time.time()
        self.signature = signature

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature
        }

    def calculate_hash(self) -> str:
        tx_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()

    def __repr__(self):
        return f"Transaction({self.sender} -> {self.recipient}: {self.amount} DPC)"

class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Transaction],
                 previous_hash: str, nonce: int = 0, difficulty: int = 2):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.difficulty = difficulty
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.hash_block()

    def hash_block(self):
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'merkle_root': self.merkle_root
        },
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def calculate_merkle_root(self) -> str:
        if not self.transactions:
            return hasher.sha256(b'').hexdigest()

        tx_hashes = [tx.calculate_hash() for tx in self.transactions]

        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            tx_hashes = new_hashes
        return tx_hashes[0]

    def mine_block(self, difficulty: int = None) -> str:
        if difficulty is None:
            difficulty = self.difficulty

        target = '0' * difficulty

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.hash_block()
        return self.hash

    def is_valid(self, previous_block: 'Block' = None) -> bool:
        if self.hash != self.hash_block():
            return False

        if self.merkle_root != self.calculate_merkle_root():
            return False

        if not self.hash.startswith('0' * self.difficulty):
            return False

        if previous_block:
            if self.previous_hash != previous_block.hash:
                return False
            if self.index != previous_block.index + 1:
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'merkle_root': self.merkle_root,
            'hash': self.hash,
            'difficulty': self.difficulty,
        }

    @classmethod
    def from_dict(cls, block_dict: Dict[str, Any]) -> 'Block':
        transactions = [Transaction(**tx_data) for tx_data in block_dict['transactions']]
        block = cls(
            index=block_dict['index'],
            timestamp=block_dict['timestamp'],
            transactions=transactions,
            previous_hash=block_dict['previous_hash'],
            nonce=block_dict['nonce'],
            difficulty=block_dict.get('difficulty', 2)
        )
        return block

    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash[:16]}..., txs={len(self.transactions)})"